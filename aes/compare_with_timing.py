from pathlib import Path
from hashlib import sha256
from time import perf_counter
from statistics import mean, median

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

# Исходная собственная реализация.
from aes import (
    encrypt_bytes as my_encrypt,
    decrypt_bytes as my_decrypt,
)

# Та же реализация, но с таблицами умножения MUL9/MUL11/MUL13/MUL14.
from aes_optimized import (
    encrypt_bytes as opt_encrypt,
    decrypt_bytes as opt_decrypt,
)


# Впиши сюда свой ключ: ровно 32 hex-символа.
KEY_HEX = "6c6f6b69747269636b73746572646f67"

INPUT_FILE = Path("loki.png")
REPEATS = 5


def get_key() -> bytes:
    try:
        key = bytes.fromhex(KEY_HEX)
    except ValueError as exc:
        raise ValueError(
            "KEY_HEX должен содержать только hex-символы 0-9, a-f"
        ) from exc

    if len(key) != 16:
        raise ValueError("Для AES-128 нужен ключ из 32 hex-символов (16 байт)")

    return key


def lib_encrypt(data: bytes, key: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(pad(data, AES.block_size))


def lib_decrypt(data: bytes, key: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_ECB)
    return unpad(cipher.decrypt(data), AES.block_size)


def measure(func, *args):
    times = []
    result = None

    for _ in range(REPEATS):
        start = perf_counter()
        result = func(*args)
        times.append(perf_counter() - start)

    return result, times


def print_measurement(name: str, times: list[float]) -> None:
    print(f"{name:<32}среднее = {mean(times):.6f} с, медиана = {median(times):.6f} с")


def main() -> None:
    key = get_key()
    original = INPUT_FILE.read_bytes()

    # ---------------- ШИФРОВАНИЕ ----------------

    my_encrypted, my_enc_times = measure(my_encrypt, original, key)
    opt_encrypted, opt_enc_times = measure(opt_encrypt, original, key)
    lib_encrypted, lib_enc_times = measure(lib_encrypt, original, key)

    # ---------------- ДЕШИФРОВАНИЕ ----------------

    my_decrypted, my_dec_times = measure(my_decrypt, my_encrypted, key)

    opt_decrypted, opt_dec_times = measure(opt_decrypt, opt_encrypted, key)

    lib_decrypted, lib_dec_times = measure(lib_decrypt, lib_encrypted, key)

    # ---------------- КОРРЕКТНОСТЬ ----------------

    print("=== ПРОВЕРКА ШИФРОВАНИЯ ===")

    print(
        "Исходный AES == оптимизированный:",
        my_encrypted == opt_encrypted,
    )
    print(
        "Исходный AES == PyCryptodome:     ",
        my_encrypted == lib_encrypted,
    )
    print(
        "Оптимизированный == PyCryptodome: ",
        opt_encrypted == lib_encrypted,
    )

    print("\nSHA-256 шифротекста:")
    print("Исходный AES:        ", sha256(my_encrypted).hexdigest())
    print("Оптимизированный AES:", sha256(opt_encrypted).hexdigest())
    print("PyCryptodome:        ", sha256(lib_encrypted).hexdigest())

    print("\n=== ПРОВЕРКА ДЕШИФРОВАНИЯ ===")

    print(
        "Исходный AES восстановил оригинал:       ",
        my_decrypted == original,
    )
    print(
        "Оптимизированный AES восстановил оригинал:",
        opt_decrypted == original,
    )
    print(
        "PyCryptodome восстановил оригинал:       ",
        lib_decrypted == original,
    )

    print(
        "Все три результата дешифрования совпадают:",
        my_decrypted == opt_decrypted == lib_decrypted,
    )

    # ---------------- ВРЕМЯ ----------------

    print(f"\n=== ВРЕМЯ ШИФРОВАНИЯ ({REPEATS} запусков) ===")
    print_measurement("Мой AES:", my_enc_times)
    print_measurement("Мой AES + таблицы:", opt_enc_times)
    print_measurement("PyCryptodome:", lib_enc_times)

    print(f"\n=== ВРЕМЯ ДЕШИФРОВАНИЯ ({REPEATS} запусков) ===")
    print_measurement("Мой AES:", my_dec_times)
    print_measurement("Мой AES + таблицы:", opt_dec_times)
    print_measurement("PyCryptodome:", lib_dec_times)

    my_enc = mean(my_enc_times)
    opt_enc = mean(opt_enc_times)
    lib_enc = mean(lib_enc_times)

    my_dec = mean(my_dec_times)
    opt_dec = mean(opt_dec_times)
    lib_dec = mean(lib_dec_times)

    print("\n=== ЭФФЕКТ ОПТИМИЗАЦИИ ===")

    print(f"Ускорение собственного шифрования:   {my_enc / opt_enc:.2f}x")
    print(f"Ускорение собственного дешифрования: {my_dec / opt_dec:.2f}x")

    print("\n=== СРАВНЕНИЕ С PYCRYPTODOME ===")

    print(f"PyCryptodome быстрее исходного шифрования:       {my_enc / lib_enc:.2f}x")
    print(
        f"PyCryptodome быстрее оптимизированного шифрования: {opt_enc / lib_enc:.2f}x"
    )

    print(f"PyCryptodome быстрее исходного дешифрования:       {my_dec / lib_dec:.2f}x")
    print(
        f"PyCryptodome быстрее оптимизированного дешифрования: {opt_dec / lib_dec:.2f}x"
    )

    # Сохраняем результаты, чтобы при желании можно было открыть их вручную.
    Path("my.enc").write_bytes(my_encrypted)
    Path("optimized.enc").write_bytes(opt_encrypted)
    Path("library.enc").write_bytes(lib_encrypted)

    Path("my_decrypted_loki.png").write_bytes(my_decrypted)
    Path("optimized_decrypted_loki.png").write_bytes(opt_decrypted)
    Path("library_decrypted_loki.png").write_bytes(lib_decrypted)


if __name__ == "__main__":
    main()
