#!/usr/bin/env python3
"""Учебная реализация ГОСТ 34.11-2018 (Стрибог), Python 3.9+.

Внутри используются векторы в порядке записи стандарта (big-endian).
Обычный байтовый интерфейс streebog() переводит их в потоковый порядок.
Внешние библиотеки не нужны. Файлы читаются целиком в память.
"""

import argparse
from pathlib import Path

PI = (
    252,
    238,
    221,
    17,
    207,
    110,
    49,
    22,
    251,
    196,
    250,
    218,
    35,
    197,
    4,
    77,
    233,
    119,
    240,
    219,
    147,
    46,
    153,
    186,
    23,
    54,
    241,
    187,
    20,
    205,
    95,
    193,
    249,
    24,
    101,
    90,
    226,
    92,
    239,
    33,
    129,
    28,
    60,
    66,
    139,
    1,
    142,
    79,
    5,
    132,
    2,
    174,
    227,
    106,
    143,
    160,
    6,
    11,
    237,
    152,
    127,
    212,
    211,
    31,
    235,
    52,
    44,
    81,
    234,
    200,
    72,
    171,
    242,
    42,
    104,
    162,
    253,
    58,
    206,
    204,
    181,
    112,
    14,
    86,
    8,
    12,
    118,
    18,
    191,
    114,
    19,
    71,
    156,
    183,
    93,
    135,
    21,
    161,
    150,
    41,
    16,
    123,
    154,
    199,
    243,
    145,
    120,
    111,
    157,
    158,
    178,
    177,
    50,
    117,
    25,
    61,
    255,
    53,
    138,
    126,
    109,
    84,
    198,
    128,
    195,
    189,
    13,
    87,
    223,
    245,
    36,
    169,
    62,
    168,
    67,
    201,
    215,
    121,
    214,
    246,
    124,
    34,
    185,
    3,
    224,
    15,
    236,
    222,
    122,
    148,
    176,
    188,
    220,
    232,
    40,
    80,
    78,
    51,
    10,
    74,
    167,
    151,
    96,
    115,
    30,
    0,
    98,
    68,
    26,
    184,
    56,
    130,
    100,
    159,
    38,
    65,
    173,
    69,
    70,
    146,
    39,
    94,
    85,
    47,
    140,
    163,
    165,
    125,
    105,
    213,
    149,
    59,
    7,
    88,
    179,
    64,
    134,
    172,
    29,
    247,
    48,
    55,
    107,
    228,
    136,
    217,
    231,
    137,
    225,
    27,
    131,
    73,
    76,
    63,
    248,
    254,
    141,
    83,
    170,
    144,
    202,
    216,
    133,
    97,
    32,
    113,
    103,
    164,
    45,
    43,
    9,
    91,
    203,
    155,
    37,
    208,
    190,
    229,
    108,
    82,
    89,
    166,
    116,
    210,
    230,
    244,
    180,
    192,
    209,
    102,
    175,
    194,
    57,
    75,
    99,
    182,
)

TAU = tuple((i % 8) * 8 + i // 8 for i in range(64))

A = tuple(
    int(x, 16)
    for x in """
8e20faa72ba0b470 47107ddd9b505a38 ad08b0e0c3282d1c d8045870ef14980e
6c022c38f90a4c07 3601161cf205268d 1b8e0b0e798c13c8 83478b07b2468764
a011d380818e8f40 5086e740ce47c920 2843fd2067adea10 14aff010bdd87508
0ad97808d06cb404 05e23c0468365a02 8c711e02341b2d01 46b60f011a83988e
90dab52a387ae76f 486dd4151c3dfdb9 24b86a840e90f0d2 125C354207487869
092e94218d243cba 8a174a9ec8121e5d 4585254f64090fa0 accc9ca9328a8950
9d4df05d5f661451 C0a878a0a1330aa6 60543c50de970553 302a1e286fc58ca7
18150f14b9ec46dd 0c84890ad27623e0 0642ca05693b9f70 0321658cba93c138
86275df09ce8aaa8 439da0784e745554 afc0503c273aa42a d960281e9d1d5215
e230140fc0802984 71180a8960409a42 b60c05ca30204d21 5b068c651810a89e
456c34887a3805b9 ac361a443d1c8cd2 561b0d22900e4669 2b838811480723ba
9bcf4486248d9f5d c3e9224312c8c1a0 effa11af0964ee50 f97d86d98a327728
e4fa2054a80b329c 727d102a548b194e 39b008152acb8227 9258048415eb419d
492c024284fbaec0 aa16012142f35760 550b8e9e21f7a530 a48b474f9ef5dc18
70a6a56e2440598e 3853dc371220a247 1ca76e95091051ad 0edd37c48a08a6d8
07e095624504536c 8d70c431ac02a736 c83862965601dd1b 641c314b2b8ee083
""".split()
)

C = tuple(
    bytes.fromhex(x)
    for x in (
        "b1085bda1ecadae9ebcb2f81c0657c1f2f6a76432e45d016714eb88d7585c4fc4b7ce09192676901a2422a08a460d31505767436cc744d23dd806559f2a64507",
        "6fa3b58aa99d2f1a4fe39d460f70b5d7f3feea720a232b9861d55e0f16b501319ab5176b12d699585cb561c2db0aa7ca55dda21bd7cbcd56e679047021b19bb7",
        "f574dcac2bce2fc70a39fc286a3d843506f15e5f529c1f8bf2ea7514b1297b7bd3e20fe490359eb1c1c93a376062db09c2b6f443867adb31991e96f50aba0ab2",
        "ef1fdfb3e81566d2f948e1a05d71e4dd488e857e335c3c7d9d721cad685e353fa9d72c82ed03d675d8b71333935203be3453eaa193e837f1220cbebc84e3d12e",
        "4bea6bacad4747999a3f410c6ca923637f151c1f1686104a359e35d7800fffbdbfcd1747253af5a3dfff00b723271a167a56a27ea9ea63f5601758fd7c6cfe57",
        "ae4faeae1d3ad3d96fa4c33b7a3039c02d66c4f95142a46c187f9ab49af08ec6cffaa6b71c9ab7b40af21f66c2bec6b6bf71c57236904f35fa68407a46647d6e",
        "f4c70e16eeaac5ec51ac86febf240954399ec6c7e6bf87c9d3473e33197a93c90992abc52d822c3706476983284a05043517454ca23c4af38886564d3a14d493",
        "9b1f5b424d93c9a703e7aa020c6e41414eb7f8719c36de1e89b4443b4ddbc49af4892bcb929b069069d18d2bd1a5c42f36acc2355951a8d9a47f0dd4bf02e71e",
        "378f5a541631229b944c9ad8ec165fde3a7d3a1b258942243cd955b7e00d0984800a440bdbb2ceb17b2b8a9aa6079c540e38dc92cb1f2a607261445183235adb",
        "abbedea680056f52382ae548b2e4f3f38941e71cff8a78db1fffe18a1b3361039fe76702af69334b7a1e6c303b7652f43698fad1153bb6c374b4c7fb98459ced",
        "7bcd9ed0efc889fb3002c6cd635afe94d8fa6bbbebab076120018021148466798a1d71efea48b9caefbacd1d7d476e98dea2594ac06fd85d6bcaa4cd81f32d1b",
        "378ee767f11631bad21380b00449b17acda43c32bcdf1d77f82012d430219f9b5d80ef9d1891cc86e71da4aa88e12852faf417d5d9b21b9948bc924af11bd720",
    )
)

ZERO = bytes(64)
MASK = (1 << 512) - 1


def xor(a: bytes, b: bytes) -> bytes:
    """Побитовое сложение двух 512-битных векторов по модулю 2."""
    return bytes(x ^ y for x, y in zip(a, b))


def S(data: bytes) -> bytes:
    """Заменяем каждый байт по таблице PI, раздел 5.2."""
    return bytes(PI[x] for x in data)


def P(data: bytes) -> bytes:
    """Переставляем байты по таблице TAU, раздел 5.3."""
    return bytes(data[i] for i in TAU)


def L(data: bytes) -> bytes:
    """Умножаем каждую 64-битную часть на матрицу A над GF(2)."""
    result = bytearray()
    for offset in range(0, 64, 8):
        word = int.from_bytes(data[offset : offset + 8], "big")
        value = 0
        for bit in range(64):
            if word & (1 << (63 - bit)):
                value ^= A[bit]
        result.extend(value.to_bytes(8, "big"))
    return bytes(result)


def lps(data: bytes) -> bytes:
    """Композиция: сначала S, потом P, потом L."""
    return L(P(S(data)))


def E(key: bytes, message: bytes) -> bytes:
    """12 раундов преобразования E из раздела 7."""
    state = message
    for constant in C:
        state = lps(xor(state, key))
        key = lps(xor(key, constant))
    return xor(state, key)


def g(h: bytes, message: bytes, n: int) -> bytes:
    """Функция сжатия g_N(h, m) = E(LPS(h XOR N), m) XOR h XOR m."""
    key = lps(xor(h, n.to_bytes(64, "big")))
    return xor(xor(E(key, message), h), message)


def hash_vector(message: bytes, bits: int = 512, bit_length=None) -> bytes:
    """Хеш в порядке записи векторов из PDF.

    message: вектор старшими байтами вперёд, как в приложении А.
    bit_length: длина в битах; значащие биты выровнены вправо.
    Если не задана, учитываются все биты message, включая ведущие нули.
    """
    if bits not in (256, 512):
        raise ValueError("Длина хеша должна быть 256 или 512 бит")
    length = len(message) * 8 if bit_length is None else bit_length
    if not isinstance(length, int) or not 0 <= length <= len(message) * 8:
        raise ValueError("Некорректная длина сообщения в битах")
    value = int.from_bytes(message, "big")
    if value.bit_length() > length or length >= 1 << 512:
        raise ValueError("Сообщение не помещается в указанную длину")

    h = ZERO if bits == 512 else bytes([1]) * 64
    n = 0
    sigma = 0
    # По стандарту отделяем полные блоки справа.
    while length >= 512:
        block_value = value & MASK
        block = block_value.to_bytes(64, "big")
        h = g(h, block, n)
        n = (n + 512) & MASK
        sigma = (sigma + block_value) & MASK
        value >>= 512
        length -= 512

    # Добавляем слева единицу, остальную часть блока заполняем нулями.
    # При длине, кратной 512, здесь создаётся отдельный блок дополнения.
    block_value = (1 << length) | value
    h = g(h, block_value.to_bytes(64, "big"), n)
    n = (n + length) & MASK
    sigma = (sigma + block_value) & MASK
    h = g(h, n.to_bytes(64, "big"), 0)
    h = g(h, sigma.to_bytes(64, "big"), 0)
    return h if bits == 512 else h[:32]


def streebog(data: bytes, bits: int = 512) -> bytes:
    """Обычный байтовый интерфейс для текста и файлов.

    Развороты переводят поток байтов в запись векторов стандарта и обратно.
    """
    return hash_vector(data[::-1], bits)[::-1]


def self_test() -> None:
    """Оба сообщения приложения А, каждый в двух режимах."""
    vectors = [
        (
            "32313039383736353433323130393837363534333231303938373635343332"
            "3130393837363534333231303938373635343332313039383736353433323130",
            "486f64c1917879417fef082b3381a4e211c324f074654c38823a7b76f830ad00"
            "fa1fbae42b1285c0352f227524bc9ab16254288dd6863dccd5b9f54a1ad0541b",
            "00557be5e584fd52a449b16b0251d05d27f94ab76cbaa6da890b59d8ef1e159d",
        ),
        (
            "fbe2e5f0eee3c820fbeafaebef20fffbf0e1e0f0f520e0ed20e8ece0ebe5f0f2f120fff0eeec20f1"
            "20faf2fee5e2202ce8f6f3ede220e8e6eee1e8f0f2d1202ce8f0f2e5e220e5d1",
            "28fbc9bada033b1460642bdcddb90c3fb3e56c497ccd0f62b8a2ad4935e85f03"
            "7613966de4ee00531ae60f3b5a47f8dae06915d5f2f194996fcabf2622e6881e",
            "508f7e553c06501d749a66fc28c6cac0b005746d97537fa85d9e40904efed29d",
        ),
    ]
    for index, (message, h512, h256) in enumerate(vectors, 1):
        for bits, expected in ((512, h512), (256, h256)):
            actual = hash_vector(bytes.fromhex(message), bits).hex()
            if actual != expected:
                raise RuntimeError(
                    f"Пример {index}, {bits} бит: {actual} != {expected}"
                )
            print(f"Пример {index}, {bits} бит: OK")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--text", help="Текст, кодируется в UTF-8")
    source.add_argument("--file", type=Path, help="Файл для хеширования")
    source.add_argument("--hex", dest="hex_data", help="Байты в hex")
    parser.add_argument("--bits", type=int, choices=(256, 512), default=512)
    parser.add_argument(
        "--vector",
        action="store_true",
        help="Ввод и вывод в порядке векторов PDF; только с --hex",
    )
    parser.add_argument(
        "--bit-length", type=int, help="Длина вектора в битах; только с --vector"
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if args.vector and args.hex_data is None:
        parser.error("--vector требует --hex")
    if args.bit_length is not None and not args.vector:
        parser.error("--bit-length требует --vector")
    try:
        if args.file is not None:
            data = args.file.read_bytes()
        elif args.hex_data is not None:
            data = bytes.fromhex(args.hex_data)
        else:
            text = args.text if args.text is not None else input("Введите текст: ")
            data = text.encode("utf-8")
        if args.vector:
            result = hash_vector(data, args.bits, args.bit_length)
        else:
            result = streebog(data, args.bits)
    except (OSError, ValueError) as error:
        parser.exit(1, f"Ошибка: {error}\n")
    print(result.hex())


if __name__ == "__main__":
    main()
