import math

import numpy as np
from scipy.special import gammaincc


BLOCK_SIZE = 8
ROUNDS = 8
MASK = 0xFFFFFFFF
ALPHA = 0.01


# ============================================================
# Сеть Фейстеля
# ============================================================


def f(right, key):
    """Раундовая функция."""
    return ((right + key) ^ (right << 3)) & MASK


def round_keys(key):
    """Создание восьми раундовых ключей."""
    return [(key + i * 1234567) & MASK for i in range(ROUNDS)]


def encrypt_block(block, keys):
    """Шифрование одного 8-байтового блока."""

    # Первые четыре байта — L, остальные — R.
    left = int.from_bytes(block[:4], "big")
    right = int.from_bytes(block[4:], "big")

    for key in keys:
        left, right = right, left ^ f(right, key)

    return left.to_bytes(4, "big") + right.to_bytes(4, "big")


def decrypt_block(block, keys):
    """Расшифрование одного 8-байтового блока."""

    left = int.from_bytes(block[:4], "big")
    right = int.from_bytes(block[4:], "big")

    for key in reversed(keys):
        left, right = right ^ f(left, key), left

    return left.to_bytes(4, "big") + right.to_bytes(4, "big")


def add_padding(data):
    """Дополнение данных до размера, кратного 8."""
    count = BLOCK_SIZE - len(data) % BLOCK_SIZE
    return data + bytes([count]) * count


def remove_padding(data):
    """Удаление дополнения."""

    count = data[-1]

    if count < 1 or count > BLOCK_SIZE:
        raise ValueError("Неверный ключ или повреждённый файл")

    if data[-count:] != bytes([count]) * count:
        raise ValueError("Неверный ключ или повреждённый файл")

    return data[:-count]


def encrypt(data, key):
    """Шифрование всех данных."""

    data = add_padding(data)
    keys = round_keys(key)
    result = bytearray()

    for i in range(0, len(data), BLOCK_SIZE):
        block = data[i : i + BLOCK_SIZE]
        result.extend(encrypt_block(block, keys))

    return bytes(result)


def decrypt(data, key):
    """Расшифрование всех данных."""

    if len(data) == 0 or len(data) % BLOCK_SIZE != 0:
        raise ValueError("Некорректный размер файла")

    keys = round_keys(key)
    result = bytearray()

    for i in range(0, len(data), BLOCK_SIZE):
        block = data[i : i + BLOCK_SIZE]
        result.extend(decrypt_block(block, keys))

    return remove_padding(bytes(result))


# ============================================================
# Преобразование байтов в биты
# ============================================================


def bytes_to_bits(data):
    bits = []

    for byte in data:
        for position in range(7, -1, -1):
            bits.append((byte >> position) & 1)

    return bits


# ============================================================
# 1. Частотный тест
# ============================================================


def frequency_test(bits):
    """
    Проверяет, примерно ли поровну нулей и единиц.
    """

    n = len(bits)
    total = 0

    for bit in bits:
        if bit == 1:
            total += 1
        else:
            total -= 1

    statistic = abs(total) / math.sqrt(n)
    return math.erfc(statistic / math.sqrt(2))


# ============================================================
# 2. Частотный тест внутри блоков
# ============================================================


def block_frequency_test(bits, block_size=128):
    """
    Проверяет долю единиц внутри отдельных блоков.
    """

    number_of_blocks = len(bits) // block_size

    if number_of_blocks == 0:
        raise ValueError("Слишком мало данных для блочного теста")

    value = 0

    for i in range(number_of_blocks):
        start = i * block_size
        block = bits[start : start + block_size]

        proportion = sum(block) / block_size
        value += (proportion - 0.5) ** 2

    chi_square = 4 * block_size * value

    return float(gammaincc(number_of_blocks / 2, chi_square / 2))


# ============================================================
# 3. Тест серий
# ============================================================


def runs_test(bits):
    """
    Проверяет количество чередующихся серий нулей и единиц.
    """

    n = len(bits)
    proportion = sum(bits) / n

    # Если нулей и единиц недостаточно поровну,
    # тест серий автоматически не пройден.
    if abs(proportion - 0.5) >= 2 / math.sqrt(n):
        return 0.0

    runs = 1

    for i in range(1, n):
        if bits[i] != bits[i - 1]:
            runs += 1

    expected = 2 * n * proportion * (1 - proportion)

    denominator = 2 * math.sqrt(2 * n) * proportion * (1 - proportion)

    return math.erfc(abs(runs - expected) / denominator)


# ============================================================
# 4. Спектральный тест
# ============================================================


def spectral_test(bits):
    """
    Ищет повторяющиеся периодические структуры
    с помощью преобразования Фурье.
    """

    n = len(bits)

    # Нули превращаем в -1, единицы — в +1.
    values = np.array([1 if bit == 1 else -1 for bit in bits])

    spectrum = np.fft.fft(values)

    # Используем первую половину спектра.
    magnitudes = np.abs(spectrum[: n // 2])

    threshold = math.sqrt(math.log(1 / 0.05) * n)

    expected_below = 0.95 * n / 2
    actual_below = np.sum(magnitudes < threshold)

    statistic = (actual_below - expected_below) / math.sqrt(n * 0.95 * 0.05 / 4)

    return math.erfc(abs(statistic) / math.sqrt(2))


# ============================================================
# Запуск тестов
# ============================================================


def print_result(name, p_value):
    if p_value >= ALPHA:
        result = "ПРОЙДЕН"
    else:
        result = "НЕ ПРОЙДЕН"

    print(f"{name}:")
    print(f"  P-value: {p_value:.6f}")
    print(f"  {result}")
    print()


def test_data(data):
    """Запускает четыре статистических теста."""

    if len(data) < 16:
        raise ValueError("Для тестирования нужно не менее 16 байтов")

    bits = bytes_to_bits(data)

    print("\nСтатистическое тестирование")
    print(f"Байтов: {len(data)}")
    print(f"Битов: {len(bits)}")
    print(f"Уровень значимости: {ALPHA}\n")

    print_result(
        "1. Частотный тест",
        frequency_test(bits),
    )

    print_result(
        "2. Частотный тест внутри блоков",
        block_frequency_test(bits),
    )

    print_result(
        "3. Тест серий",
        runs_test(bits),
    )

    print_result(
        "4. Спектральный тест",
        spectral_test(bits),
    )


def test_file(filename):
    with open(filename, "rb") as file:
        data = file.read()

    test_data(data)


# ============================================================
# Основная программа
# ============================================================


def main():
    print("1 — зашифровать файл")
    print("2 — расшифровать файл")
    print("3 — проверить файл тестами NIST")

    choice = input("Выберите действие: ")

    if choice == "1":
        input_name = input("Исходный файл: ")
        output_name = input("Зашифрованный файл: ")
        key = int(input("Целочисленный ключ: "))

        with open(input_name, "rb") as file:
            data = file.read()

        result = encrypt(data, key)

        with open(output_name, "wb") as file:
            file.write(result)

        print("Файл зашифрован")

        # Автоматически тестируем шифротекст.
        test_data(result)

    elif choice == "2":
        input_name = input("Зашифрованный файл: ")
        output_name = input("Расшифрованный файл: ")
        key = int(input("Целочисленный ключ: "))

        with open(input_name, "rb") as file:
            data = file.read()

        result = decrypt(data, key)

        with open(output_name, "wb") as file:
            file.write(result)

        print("Файл расшифрован")

    elif choice == "3":
        filename = input("Проверяемый файл: ")
        test_file(filename)

    else:
        print("Неизвестная команда")


if __name__ == "__main__":
    main()
