from pathlib import Path


S_BOX = bytes.fromhex(
    "63 7c 77 7b f2 6b 6f c5 30 01 67 2b fe d7 ab 76 "
    "ca 82 c9 7d fa 59 47 f0 ad d4 a2 af 9c a4 72 c0 "
    "b7 fd 93 26 36 3f f7 cc 34 a5 e5 f1 71 d8 31 15 "
    "04 c7 23 c3 18 96 05 9a 07 12 80 e2 eb 27 b2 75 "
    "09 83 2c 1a 1b 6e 5a a0 52 3b d6 b3 29 e3 2f 84 "
    "53 d1 00 ed 20 fc b1 5b 6a cb be 39 4a 4c 58 cf "
    "d0 ef aa fb 43 4d 33 85 45 f9 02 7f 50 3c 9f a8 "
    "51 a3 40 8f 92 9d 38 f5 bc b6 da 21 10 ff f3 d2 "
    "cd 0c 13 ec 5f 97 44 17 c4 a7 7e 3d 64 5d 19 73 "
    "60 81 4f dc 22 2a 90 88 46 ee b8 14 de 5e 0b db "
    "e0 32 3a 0a 49 06 24 5c c2 d3 ac 62 91 95 e4 79 "
    "e7 c8 37 6d 8d d5 4e a9 6c 56 f4 ea 65 7a ae 08 "
    "ba 78 25 2e 1c a6 b4 c6 e8 dd 74 1f 4b bd 8b 8a "
    "70 3e b5 66 48 03 f6 0e 61 35 57 b9 86 c1 1d 9e "
    "e1 f8 98 11 69 d9 8e 94 9b 1e 87 e9 ce 55 28 df "
    "8c a1 89 0d bf e6 42 68 41 99 2d 0f b0 54 bb 16"
)


INV_S_BOX = bytes([next(i for i, value in enumerate(S_BOX) if value == x) for x in range(256)])


RCON = (0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1B, 0x36)


def key_expansion(key: bytes) -> list[list[int]]:
    """Разворачивает 16 байт ключа в таблицу из 4 строк и 44 колонок."""
    if len(key) != 16:
        raise ValueError("AES-128 key must be 16 bytes")

    schedule = make_state(key)
    for c in range(4, 44):
        word = [schedule[r][c - 1] for r in range(4)]
        if c % 4 == 0:
            # RotWord, SubWord и XOR с константой текущего раунда.
            word = word[1:] + word[:1]
            word = [S_BOX[value] for value in word]
            word[0] ^= RCON[c // 4 - 1]
        for r in range(4):
            schedule[r].append(schedule[r][c - 4] ^ word[r])
    return schedule


def add_round_key(
    state: list[list[int]], key_schedule: list[list[int]], round_number: int
) -> list[list[int]]:
    return [
        [state[r][c] ^ key_schedule[r][4 * round_number + c] for c in range(4)]
        for r in range(4)
    ]


def sub_bytes(state: list[list[int]]) -> list[list[int]]:
    return [[S_BOX[value] for value in row] for row in state]


def shift_rows(state: list[list[int]]):
    return [state[row][row:] + state[row][:row] for row in range(4)]


def mul2(value: int) -> int:
    result = value << 1
    if value & 0x80:
        result ^= 0x1B
    return result & 0xFF


def mul3(value: int) -> int:
    return mul2(value) ^ value


def mix_cols(state: list[list[int]]) -> list[list[int]]:
    result = [[0] * 4 for _ in range(4)]

    for c in range(4):
        a, b, d, e = [state[r][c] for r in range(4)]

        result[0][c] = mul2(a) ^ mul3(b) ^ d ^ e
        result[1][c] = a ^ mul2(b) ^ mul3(d) ^ e
        result[2][c] = a ^ b ^ mul2(d) ^ mul3(e)
        result[3][c] = mul3(a) ^ b ^ d ^ mul2(e)

    return result



def inv_sub_bytes(state: list[list[int]]) -> list[list[int]]:
    return [[INV_S_BOX[value] for value in row] for row in state]


def inv_shift_rows(state: list[list[int]]) -> list[list[int]]:
    return [state[row][-row:] + state[row][:-row] if row else state[row][:] for row in range(4)]


def gmul(a: int, b: int) -> int:
    result = 0
    for _ in range(8):
        if b & 1:
            result ^= a
        high_bit = a & 0x80
        a = (a << 1) & 0xFF
        if high_bit:
            a ^= 0x1B
        b >>= 1
    return result


# Таблицы умножения для обратного MixColumns.
# Они вычисляются один раз при запуске программы.
MUL9 = tuple(gmul(value, 9) for value in range(256))
MUL11 = tuple(gmul(value, 11) for value in range(256))
MUL13 = tuple(gmul(value, 13) for value in range(256))
MUL14 = tuple(gmul(value, 14) for value in range(256))


def inv_mix_cols(state: list[list[int]]) -> list[list[int]]:
    result = [[0] * 4 for _ in range(4)]
    for c in range(4):
        a, b, d, e = [state[r][c] for r in range(4)]
        result[0][c] = MUL14[a] ^ MUL11[b] ^ MUL13[d] ^ MUL9[e]
        result[1][c] = MUL9[a] ^ MUL14[b] ^ MUL11[d] ^ MUL13[e]
        result[2][c] = MUL13[a] ^ MUL9[b] ^ MUL14[d] ^ MUL11[e]
        result[3][c] = MUL11[a] ^ MUL13[b] ^ MUL9[d] ^ MUL14[e]
    return result


def make_state(block: bytes) -> list[list[int]]:
    if len(block) != 16:
        raise ValueError("block must be 16 bytes")
    return [[block[r + 4 * c] for c in range(4)] for r in range(4)]


def state_to_bytes(state: list[list[int]]) -> bytes:
    return bytes(state[r][c] for c in range(4) for r in range(4))


def _encrypt_block(block: bytes, key_schedule: list[list[int]]) -> bytes:
    state = add_round_key(make_state(block), key_schedule, 0)
    for round_number in range(1, 10):
        state = sub_bytes(state)
        state = shift_rows(state)
        state = mix_cols(state)
        state = add_round_key(state, key_schedule, round_number)

    # В десятом, последнем раунде MixColumns отсутствует.
    state = sub_bytes(state)
    state = shift_rows(state)
    state = add_round_key(state, key_schedule, 10)
    return state_to_bytes(state)



def _decrypt_block(block: bytes, key_schedule: list[list[int]]) -> bytes:
    state = add_round_key(make_state(block), key_schedule, 10)

    for round_number in range(9, 0, -1):
        state = inv_shift_rows(state)
        state = inv_sub_bytes(state)
        state = add_round_key(state, key_schedule, round_number)
        state = inv_mix_cols(state)

    state = inv_shift_rows(state)
    state = inv_sub_bytes(state)
    state = add_round_key(state, key_schedule, 0)
    return state_to_bytes(state)


def decrypt_block(block: bytes, key: bytes) -> bytes:
    """Расшифровывает один блок AES-128 без padding."""
    return _decrypt_block(block, key_expansion(key))


def encrypt_block(block: bytes, key: bytes) -> bytes:
    """Шифрует один блок AES-128 без padding."""
    return _encrypt_block(block, key_expansion(key))


def pad(data: bytes, block_size: int = 16) -> bytes:
    n = block_size - len(data) % block_size
    return data + bytes([n]) * n


def unpad(data: bytes, block_size: int = 16) -> bytes:
    if not data or len(data) % block_size != 0:
        raise ValueError("incorrect data size")

    n = data[-1]
    if not 1 <= n <= block_size or data[-n:] != bytes([n]) * n:
        raise ValueError("incorrect padding")

    return data[:-n]


def encrypt_bytes(data: bytes, key: bytes) -> bytes:
    """Шифрует произвольные байты: ECB с дополнением PKCS#7."""
    data = pad(data)
    key_schedule = key_expansion(key)
    return b"".join(
        _encrypt_block(data[i:i + 16], key_schedule)
        for i in range(0, len(data), 16)
    )



def decrypt_bytes(data: bytes, key: bytes) -> bytes:
    """Расшифровывает произвольные байты: ECB с удалением PKCS#7."""
    if not data or len(data) % 16 != 0:
        raise ValueError("encrypted data size must be a multiple of 16 bytes")
    key_schedule = key_expansion(key)
    decrypted = b"".join(
        _decrypt_block(data[i:i + 16], key_schedule)
        for i in range(0, len(data), 16)
    )
    return unpad(decrypted)


def aes(message: str, key: bytes) -> bytes:
    """Шифрует текст в UTF-8."""
    return encrypt_bytes(message.encode("utf-8"), key)


def encrypt_file(source: str | Path, key: bytes) -> Path:
    """Шифрует файл целиком и сохраняет рядом новый файл с суффиксом .enc."""
    source = Path(source).expanduser()
    encrypted = encrypt_bytes(source.read_bytes(), key)
    destination = source.with_name(source.name + ".enc")
    # Не перезаписываем существующие файлы.
    with destination.open("xb") as output:
        output.write(encrypted)
    return destination



def decrypt_file(source: str | Path, key: bytes) -> Path:
    """Расшифровывает .enc-файл и сохраняет восстановленный файл рядом."""
    source = Path(source).expanduser()
    decrypted = decrypt_bytes(source.read_bytes(), key)

    if source.name.endswith(".enc"):
        original_name = source.name[:-4]
    else:
        original_name = source.name + ".dec"

    destination = source.with_name("decrypted_" + original_name)
    with destination.open("xb") as output:
        output.write(decrypted)
    return destination


def main() -> None:
    while True:
        print("choose operating mode:\n1 - encrypt text\n2 - encrypt file\n3 - decrypt file\n0 - exit")
        mode = input(": ")
        if mode == "0":
            break
        if mode == "1":
            message = input("message: ")
            key = input("key (32 hex digits): ")
            try:
                enc_message = aes(message, bytes.fromhex(key))
            except ValueError as error:
                print(f"error: {error}")
                continue
            print(f"res: {enc_message.hex()}")
        elif mode == "2":
            source = input("image/file path: ")
            key = input("key (32 hex digits): ")
            try:
                destination = encrypt_file(source, bytes.fromhex(key))
            except (ValueError, OSError) as error:
                print(f"error: {error}")
                continue
            print(f"saved: {destination}")
        elif mode == "3":
            source = input("encrypted file path: ")
            key = input("key (32 hex digits): ")
            try:
                destination = decrypt_file(source, bytes.fromhex(key))
            except (ValueError, OSError) as error:
                print(f"error: {error}")
                continue
            print(f"saved: {destination}")
        else:
            print("try again")


if __name__ == "__main__":
    main()
