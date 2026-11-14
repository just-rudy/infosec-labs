import math

from scipy.special import gammaincc


N = 256
ALPHA = 0.01


def create_s(key: bytes) -> list[int]:
    s = list(range(N))
    j = 0

    for i in range(N):
        j = (j + s[i] + key[i % len(key)]) % N
        s[i], s[j] = s[j], s[i]

    return s


def generate_gamma(s: list[int], length: int) -> bytes:
    gamma = bytearray()

    i = 0
    j = 0

    for _ in range(length):
        i = (i + 1) % N
        j = (j + s[i]) % N

        s[i], s[j] = s[j], s[i]

        index = (s[i] + s[j]) % N
        gamma.append(s[index])

    return bytes(gamma)


def rc4(data: bytes, key: bytes) -> bytes:
    if len(key) == 0:
        raise ValueError("Ключ не должен быть пустым")

    s = create_s(key)
    gamma = generate_gamma(s, len(data))

    result = bytearray()

    for data_byte, gamma_byte in zip(data, gamma):
        result.append(data_byte ^ gamma_byte)

    return bytes(result)


def process_file(
    input_filename: str,
    output_filename: str,
    key: bytes,
) -> None:
    with open(input_filename, "rb") as file:
        data = file.read()

    result = rc4(data, key)

    with open(output_filename, "wb") as file:
        file.write(result)


def create_gamma_file(
    filename: str,
    size: int,
    key: bytes,
) -> None:

    s = create_s(key)
    gamma = generate_gamma(s, size)

    with open(filename, "wb") as file:
        file.write(gamma)


# Преобразование файла в последовательность битов
def bytes_to_bits(data: bytes) -> list[int]:
    bits = []

    for byte in data:
        for position in range(7, -1, -1):
            bit = (byte >> position) & 1
            bits.append(bit)

    return bits


# Тест 1. Частотный тест
def frequency_test(bits: list[int]) -> float:
    """
    Проверяет, примерно ли одинаково количество нулей и единиц.
    Возвращает P-value.
    """

    n = len(bits)

    # 0 превращаем в -1, а 1 оставляем как +1.
    total = 0

    for bit in bits:
        if bit == 1:
            total += 1
        else:
            total -= 1

    statistic = abs(total) / math.sqrt(n)

    p_value = math.erfc(statistic / math.sqrt(2))

    return p_value


# Тест 2. Частотный тест внутри блоков
def block_frequency_test(
    bits: list[int],
    block_size: int = 128,
) -> float:
    """
    Разделяет последовательность на блоки и проверяет,
    близка ли доля единиц в каждом блоке к 0.5.
    """

    n = len(bits)
    number_of_blocks = n // block_size

    if number_of_blocks == 0:
        raise ValueError("Последовательность слишком короткая для блочного теста")

    sum_of_squares = 0.0

    for block_number in range(number_of_blocks):
        start = block_number * block_size
        end = start + block_size

        block = bits[start:end]

        ones = sum(block)
        proportion = ones / block_size

        sum_of_squares += (proportion - 0.5) ** 2

    chi_square = 4 * block_size * sum_of_squares

    p_value = gammaincc(
        number_of_blocks / 2,
        chi_square / 2,
    )

    return float(p_value)


# Тест 3. Тест серий
def runs_test(bits: list[int]) -> float:
    """
    Проверяет чередование последовательностей нулей и единиц.

    Серия - непрерывная последовательность одинаковых битов.

    Например, в последовательности 1110010 находятся серии:
    111, 00, 1, 0.
    """

    n = len(bits)

    ones = sum(bits)
    proportion = ones / n

    # Предварительная проверка баланса нулей и единиц.
    limit = 2 / math.sqrt(n)

    if abs(proportion - 0.5) >= limit:
        return 0.0

    # Первая последовательность уже считается одной серией.
    number_of_runs = 1

    for i in range(1, n):
        if bits[i] != bits[i - 1]:
            number_of_runs += 1

    expected_runs = 2 * n * proportion * (1 - proportion)

    numerator = abs(number_of_runs - expected_runs)

    denominator = 2 * math.sqrt(2 * n) * proportion * (1 - proportion)

    p_value = math.erfc(numerator / denominator)

    return p_value


# Тест 4. Максимальная длина серии единиц
def longest_run_in_block(block: list[int]) -> int:
    """
    Находит максимальное количество подряд идущих единиц
    внутри одного блока.
    """

    longest = 0
    current = 0

    for bit in block:
        if bit == 1:
            current += 1
            longest = max(longest, current)
        else:
            current = 0

    return longest


def longest_run_test(bits: list[int]) -> float:
    """
    Проверяет максимальную длину серии единиц в блоках.
    Параметры выбираются по правилам NIST.
    """

    n = len(bits)

    if n < 128:
        raise ValueError("Для теста максимальной серии нужно не менее 128 бит")

    if n < 6272:
        block_size = 8

        probabilities = [
            0.2148,
            0.3672,
            0.2305,
            0.1875,
        ]

        def get_group(longest: int) -> int:
            if longest <= 1:
                return 0
            if longest == 2:
                return 1
            if longest == 3:
                return 2
            return 3

    elif n < 750000:
        block_size = 128

        probabilities = [
            0.1174,
            0.2430,
            0.2493,
            0.1752,
            0.1027,
            0.1124,
        ]

        def get_group(longest: int) -> int:
            if longest <= 4:
                return 0
            if longest == 5:
                return 1
            if longest == 6:
                return 2
            if longest == 7:
                return 3
            if longest == 8:
                return 4
            return 5

    else:
        block_size = 10000

        probabilities = [
            0.0882,
            0.2092,
            0.2483,
            0.1933,
            0.1208,
            0.0675,
            0.0727,
        ]

        def get_group(longest: int) -> int:
            if longest <= 10:
                return 0
            if longest == 11:
                return 1
            if longest == 12:
                return 2
            if longest == 13:
                return 3
            if longest == 14:
                return 4
            if longest == 15:
                return 5
            return 6

    number_of_blocks = n // block_size

    # observed[i] - количество блоков,
    # попавших в категорию i.
    observed = [0] * len(probabilities)

    for block_number in range(number_of_blocks):
        start = block_number * block_size
        end = start + block_size

        block = bits[start:end]

        longest = longest_run_in_block(block)
        group = get_group(longest)

        observed[group] += 1

    chi_square = 0.0

    for observed_count, probability in zip(
        observed,
        probabilities,
    ):
        expected_count = number_of_blocks * probability

        chi_square += (observed_count - expected_count) ** 2 / expected_count

    degrees_of_freedom = len(probabilities) - 1

    p_value = gammaincc(
        degrees_of_freedom / 2,
        chi_square / 2,
    )

    return float(p_value)


# Запуск всех четырёх тестов
def print_test_result(name: str, p_value: float) -> None:
    """
    Печатает результат одного теста.
    """

    if p_value >= ALPHA:
        result = "ПРОЙДЕН"
    else:
        result = "НЕ ПРОЙДЕН"

    print(f"{name}:")
    print(f"  P-value = {p_value:.6f}")
    print(f"  Результат: {result}")
    print()


def test_data(data: bytes) -> None:
    """
    Запускает четыре теста для переданных данных.
    """

    bits = bytes_to_bits(data)

    print()
    print(f"Количество байтов: {len(data)}")
    print(f"Количество битов:  {len(bits)}")
    print(f"Уровень значимости: {ALPHA}")
    print()

    print_test_result(
        "1. Частотный тест",
        frequency_test(bits),
    )

    print_test_result(
        "2. Частотный тест внутри блоков",
        block_frequency_test(bits),
    )

    print_test_result(
        "3. Тест серий",
        runs_test(bits),
    )

    print_test_result(
        "4. Тест максимальной серии единиц",
        longest_run_test(bits),
    )


def test_file(filename: str) -> None:
    """
    Читает бинарный файл и запускает четыре теста.
    """

    with open(filename, "rb") as file:
        data = file.read()

    if len(data) == 0:
        raise ValueError("Нельзя проверить пустой файл")

    test_data(data)


# Основная программа
def main() -> None:
    print("Выберите действие:")
    print("1 - зашифровать или расшифровать файл RC4")
    print("2 - создать гамму RC4 и выполнить тесты")
    # print("3 - проверить существующий файл")

    choice = input("Ваш выбор: ")

    if choice == "1":
        input_filename = input("Исходный файл: ")
        output_filename = input("Выходной файл: ")
        key = input("Ключ: ").encode("utf-8")

        process_file(
            input_filename,
            output_filename,
            key,
        )

        print(f"Результат записан в {output_filename}")

    elif choice == "2":
        filename = input("Имя файла с гаммой [rc4_stream.bin]: ")

        if filename == "":
            filename = "rc4_stream.bin"

        key = input("Ключ: ").encode("utf-8")

        # 125 000 байт = 1 000 000 бит.
        create_gamma_file(
            filename,
            125_000,
            key,
        )

        print(f"Гамма записана в {filename}")

        test_file(filename)

    elif choice == "3":
        filename = input("Имя проверяемого файла: ")
        test_file(filename)

    else:
        print("Неизвестная команда")


if __name__ == "__main__":
    main()
