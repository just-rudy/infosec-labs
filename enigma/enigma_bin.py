import json
import base64
import sys

ALPHABET_SIZE = 256


class Rotor:
    def __init__(self, wiring: bytes, start_pos: int):
        if len(wiring) != ALPHABET_SIZE:
            raise ValueError(
                f"Rotor wiring must contain {ALPHABET_SIZE} bytes, got {len(wiring)}"
            )

        # Проверяем, что wiring является перестановкой 0..255
        if set(wiring) != set(range(ALPHABET_SIZE)):
            raise ValueError(
                "Rotor wiring must be a permutation of all byte values 0..255"
            )

        if not 0 <= start_pos < ALPHABET_SIZE:
            raise ValueError(f"Invalid rotor start position: {start_pos}")

        self.wiring = wiring
        self.position = start_pos

    def step(self):
        self.position = (self.position + 1) % ALPHABET_SIZE


class Enigma:
    def __init__(self, rotors: list[Rotor], reflector_wiring: bytes):
        if len(rotors) != 3:
            raise ValueError("Enigma requires exactly 3 rotors")

        if len(reflector_wiring) != ALPHABET_SIZE:
            raise ValueError(f"Reflector wiring must contain {ALPHABET_SIZE} bytes")

        if set(reflector_wiring) != set(range(ALPHABET_SIZE)):
            raise ValueError(
                "Reflector wiring must be a permutation of all byte values 0..255"
            )

        self.rotors = rotors
        self.refl = reflector_wiring

    def _step_rotors(self):
        rotR, rotM, rotL = self.rotors

        rotR.step()
        # if rotR.position == rotR.turnover:
        #     rotM.step()

    def _go_left(self, value: int, rot: Rotor) -> int:
        shifted = (value + rot.position) % ALPHABET_SIZE

        routed = rot.wiring[shifted]

        return (routed - rot.position) % ALPHABET_SIZE

    def _go_right(self, value: int, rot: Rotor) -> int:

        shifted = (value + rot.position) % ALPHABET_SIZE

        # Ищем, какой вход соответствует shifted.
        routed = rot.wiring.index(shifted)

        return (routed - rot.position) % ALPHABET_SIZE

    def _reflect(self, value: int) -> int:
        return self.refl[value]

    def encrypt_byte(self, value: int) -> int:
        self._step_rotors()

        # byte -> right rotor -> middle rotor -> left rotor
        value = self._go_left(value, self.rotors[0])  # R
        value = self._go_left(value, self.rotors[1])  # M
        value = self._go_left(value, self.rotors[2])  # L

        # Reflector
        value = self._reflect(value)

        # left rotor -> middle rotor -> right rotor
        value = self._go_right(value, self.rotors[2])  # L
        value = self._go_right(value, self.rotors[1])  # M
        value = self._go_right(value, self.rotors[0])  # R

        return value

    def encrypt_data(self, data: bytes) -> bytes:
        result = bytearray()

        for byte in data:
            encrypted = self.encrypt_byte(byte)
            result.append(encrypted)

        return bytes(result)


def load_keys(filename: str = "keys.json"):
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)

    rotors_data = data["rotors"]

    if len(rotors_data) != 3:
        raise ValueError("keys.json must contain exactly 3 rotors")

    rotors = []

    for rotor_data in rotors_data:
        wiring = base64.b64decode(rotor_data["key"])

        state = rotor_data["state"]

        rotor = Rotor(wiring=wiring, start_pos=state)

        rotors.append(rotor)

    reflector = base64.b64decode(data["reflector"])

    return rotors, reflector


def encrypt_file(input_filename: str, output_filename: str):
    rotors, reflector = load_keys("keys.json")

    machine = Enigma(rotors=rotors, reflector_wiring=reflector)

    with open(input_filename, "rb") as input_file:
        data = input_file.read()

    encrypted_data = machine.encrypt_data(data)

    with open(output_filename, "wb") as output_file:
        output_file.write(encrypted_data)

    print(f"Input : {input_filename}")
    print(f"Output: {output_filename}")
    print(f"Size  : {len(data)} bytes")


def main():
    if len(sys.argv) != 3:
        print("Usage:")
        print(f"  python {sys.argv[0]} <input.bin> <output.bin>")
        sys.exit(1)

    input_filename = sys.argv[1]
    output_filename = sys.argv[2]

    encrypt_file(input_filename, output_filename)


if __name__ == "__main__":
    main()
