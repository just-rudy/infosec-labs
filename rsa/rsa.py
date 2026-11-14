import secrets


def gcd(a, b):
    while b != 0:
        a, b = b, a % b

    return a


def is_prime(n, rounds=40):
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    d = n - 1
    s = 0

    while d % 2 == 0:
        d //= 2
        s += 1

    for _ in range(rounds):
        a = secrets.randbelow(n - 3) + 2
        x = pow(a, d, n)

        if x in (1, n - 1):
            continue

        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False

    return True


def generate_prime(bits=1024):
    while True:
        n = secrets.randbits(bits)
        n |= 1 << (bits - 1)
        n |= 1

        if is_prime(n):
            return n


def rsa(M, key, N):
    return pow(M, key, N)


def extended_gcd(e, n):
    if n == 0:
        return e, 1, 0

    g, x1, y1 = extended_gcd(n, e % n)

    x = y1
    y = x1 - (e // n) * y1

    return g, x, y


def prepare_nums():
    p = generate_prime()
    q = generate_prime()

    while p == q:
        q = generate_prime()

    e = 65537

    while True:
        N = p * q
        phi = (p - 1) * (q - 1)

        if gcd(e, phi) == 1:
            break

        q = generate_prime()
        while q == p:
            q = generate_prime()

    g, x, y = extended_gcd(e, phi)
    d = x % phi

    return e, d, N


def write_number(f, number):
    length = number.bit_length()

    # Длина числа в битах, записанная в 8 байтах
    f.write(length.to_bytes(8, "big"))

    # Количество байтов для хранения числа
    byte_count = (length + 7) // 8

    if byte_count == 0:
        return

    # Добиваем нулями справа до целого байта
    padding = byte_count * 8 - length
    padded_number = number << padding

    f.write(padded_number.to_bytes(byte_count, "big"))


def read_number(f):
    length_data = f.read(8)

    if len(length_data) != 8:
        raise ValueError("Ошибка чтения длины числа")

    # Длина в битах
    length = int.from_bytes(length_data, "big")

    byte_count = (length + 7) // 8
    data = f.read(byte_count)

    if len(data) != byte_count:
        raise ValueError("Ошибка чтения числа")

    if length == 0:
        return 0

    # Убираем добивание справа
    padding = byte_count * 8 - length
    number = int.from_bytes(data, "big") >> padding

    return number


def encrypt_to_file(text, filename="code.msg"):
    print("Генерация ключей RSA...")
    e, d, N = prepare_nums()

    data = text.encode("utf-8")
    M = int.from_bytes(data, "big")

    if M >= N:
        raise ValueError("Сообщение слишком длинное для одного блока RSA")

    C = rsa(M, e, N)

    with open(filename, "wb") as f:
        write_number(f, C)
        write_number(f, d)
        write_number(f, N)

    print(f"Сообщение зашифровано в файл {filename}")


def decrypt_from_file(filename="code.msg"):
    with open(filename, "rb") as f:
        C = read_number(f)
        d = read_number(f)
        N = read_number(f)

        if f.read(1):
            raise ValueError("Лишние данные в файле")

    if N <= 1 or not 0 <= C < N:
        raise ValueError("Некорректные данные RSA")

    M = rsa(C, d, N)

    length = max(1, (M.bit_length() + 7) // 8)
    return M.to_bytes(length, "big").decode("utf-8")


def main():
    while True:
        print("\n=== RSA ===")
        print("1. Зашифровать текст в файл")
        print("2. Расшифровать текст из файла")
        print("0. Выход")

        choice = input("Выберите режим: ").strip()

        if choice == "1":
            text = input("Введите текст: ")
            filename = input("Имя выходного файла [code.msg]: ").strip() or "code.msg"

            try:
                encrypt_to_file(text, filename)
            except (OSError, ValueError) as error:
                print("Ошибка:", error)

        elif choice == "2":
            filename = (
                input("Имя файла для расшифрования [code.msg]: ").strip() or "code.msg"
            )

            try:
                text = decrypt_from_file(filename)
                print("\nРасшифрованное сообщение:")
                print(text)
            except (OSError, ValueError, UnicodeError) as error:
                print("Ошибка:", error)

        elif choice == "0":
            break

        else:
            print("Неизвестный режим")


if __name__ == "__main__":
    main()
