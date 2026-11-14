from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

KEY_HEX = "6c6f6b69747269636b73746572646f67"

INPUT_FILE = Path("loki.png")
ENCRYPTED_FILE = Path("library.enc")
DECRYPTED_FILE = Path("library_decrypted_loki.png")


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


def encrypt_file_ecb(input_path: Path, output_path: Path, key: bytes) -> None:
    """Шифрует ВЕСЬ файл AES-128-ECB + PKCS#7, как aes.py."""
    data = input_path.read_bytes()
    cipher = AES.new(key, AES.MODE_ECB)
    encrypted = cipher.encrypt(pad(data, AES.block_size))
    output_path.write_bytes(encrypted)


def decrypt_file_ecb(input_path: Path, output_path: Path, key: bytes) -> None:
    encrypted = input_path.read_bytes()
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted = unpad(cipher.decrypt(encrypted), AES.block_size)
    output_path.write_bytes(decrypted)


def main() -> None:
    key = get_key()
    encrypt_file_ecb(INPUT_FILE, ENCRYPTED_FILE, key)
    decrypt_file_ecb(ENCRYPTED_FILE, DECRYPTED_FILE, key)

    original = INPUT_FILE.read_bytes()
    decrypted = DECRYPTED_FILE.read_bytes()

    print(f"Зашифровано: {ENCRYPTED_FILE}")
    print(f"Расшифровано: {DECRYPTED_FILE}")
    print("Расшифрованный файл совпадает с оригиналом:", original == decrypted)


if __name__ == "__main__":
    main()
