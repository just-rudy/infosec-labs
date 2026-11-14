ABC = "abcdefghijklmnopqrstuvwxyz"
# rotorI = "ekmflgdqvzntowyhxuspaibrcj"
# rotorII = "ajdksiruxblhwtmcqgznpyfvoe"
# rotorIII = "bdfhjlcprtxvznyeiwgakmusqo"
# reflectr = "yruhqsldpxngokmiebfzcwvjat"


class Rotor:
    def __init__(self, wiring: str, turnover: str, start_pos: str):
        self.wiring = wiring
        self.position = ABC.index(start_pos.lower())
        self.turnover = ABC.index(turnover.lower())

    def step(self):
        self.position = (self.position + 1) % 26


rotorR = Rotor("ekmflgdqvzntowyhxuspaibrcj", "r", "q")
rotorM = Rotor("ajdksiruxblhwtmcqgznpyfvoe", "m", "u")
rotorL = Rotor("bdfhjlcprtxvznyeiwgakmusqo", "d", "c")
reflectr = "yruhqsldpxngokmiebfzcwvjat"


class Enigma:
    def __init__(self, rotors: list[Rotor], reflector_wiring: str):
        self.rotors = rotors
        self.refl = reflector_wiring

    def _step_rotors(self):
        rotL, rotM, rotR = self.rotors

        rotR.step()
        if rotR.position == rotR.turnover:
            rotM.step()

    def _char_to_int(self, c: str) -> int:
        return ABC.index(c.lower())

    def _int_to_char(self, i: int) -> str:
        return ABC[i]

    def _go_left(self, i: int, rot: Rotor) -> int:
        shifted = (i + rot.position) % 26
        rotored = ABC.index(rot.wiring[shifted])
        return (rotored - rot.position) % 26

    def _go_right(self, i: int, rot: Rotor) -> int:
        shifted = (i + rot.position) % 26
        rotored = rot.wiring.index(ABC[shifted])
        return (rotored - rot.position) % 26

    def _reflect(self, i: int) -> int:
        return ABC.index(self.refl[i])

    def encrypt_letter(self, c: str) -> str:
        self._step_rotors()

        letter = self._char_to_int(c)
        letter = self._go_left(letter, self.rotors[2])  # R
        letter = self._go_left(letter, self.rotors[1])  # M
        letter = self._go_left(letter, self.rotors[0])  # L

        letter = self._reflect(letter)

        letter = self._go_right(letter, self.rotors[0])  # L
        letter = self._go_right(letter, self.rotors[1])  # M
        letter = self._go_right(letter, self.rotors[2])  # R

        return self._int_to_char(letter)

    def encrypt_text(self, text: str) -> str:
        result = []
        for ch in text:
            if ch.lower() in ABC:
                result.append(self.encrypt_letter(ch))
            else:
                result.append(ch)
        return "".join(result)


machine = Enigma(rotors=[rotorL, rotorM, rotorR], reflector_wiring=reflectr)

text = input("text: ")
while text != "0":
    res = machine.encrypt_text(text)
    print("res: ", res)
    text = input("text: ")
