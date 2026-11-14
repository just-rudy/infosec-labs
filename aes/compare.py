from pathlib import Path
from hashlib import sha256


original = Path("loki.png").read_bytes()

my_encrypted = Path("loki.png.enc").read_bytes()
lib_encrypted = Path("library.enc").read_bytes()

my_decrypted = Path("decrypted_loki.png").read_bytes()
lib_decrypted = Path("library_decrypted_loki.png").read_bytes()


print("=== ПРОВЕРКА ШИФРОВАНИЯ ===")

print("Размер моей версии:", len(my_encrypted))
print("Размер версии библиотеки:", len(lib_encrypted))

print("SHA-256 моей версии:", sha256(my_encrypted).hexdigest())
print("SHA-256 библиотеки:  ", sha256(lib_encrypted).hexdigest())

print("Первые 32 байта:")
print("Моя:       ", my_encrypted[:32].hex())
print("Библиотека:", lib_encrypted[:32].hex())

print("Полное совпадение шифротекста:", my_encrypted == lib_encrypted)


print("\n=== ПРОВЕРКА РАСШИФРОВАНИЯ ===")

print("Мой расшифрованный файл совпадает с оригиналом:", my_decrypted == original)

print(
    "Расшифрованный библиотекой файл совпадает с оригиналом:", lib_decrypted == original
)

print(
    "Мой и библиотечный расшифрованные файлы совпадают:", my_decrypted == lib_decrypted
)

print("\nSHA-256 оригинала:              ", sha256(original).hexdigest())
print("SHA-256 моего расшифрованного:  ", sha256(my_decrypted).hexdigest())
print("SHA-256 расшифрованного библиотекой:", sha256(lib_decrypted).hexdigest())
