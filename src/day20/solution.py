# from __future__ import annotations

from dataclasses import dataclass
from typing import List

import utils


class Mixer:
    @dataclass
    class MixerValue:
        value: int
        position: int

    def __init__(self, numbers: List[int], decryption_key=1):
        self.__n_numbers = len(numbers)

        # Values and their current position in original order
        self.__values = [
            self.MixerValue(number * decryption_key, ind) for ind, number in enumerate(numbers)
        ]

        # Index of value at each position
        self.__value_indices = list(range(self.__n_numbers))

    def mix(self, iter=1):
        for __ in range(iter):
            self.mix_once()

    def mix_once(self):
        for ind, mixer_value in enumerate(self.__values):
            pos = mixer_value.position
            new_pos = self.compute_new_pos(mixer_value)

            # Update positions of all "in-between" values that need to be shifted
            min_pos = min(pos, new_pos)
            max_pos = max(pos, new_pos)
            if pos < new_pos:
                # moved right
                self.__value_indices[min_pos:max_pos] = self.__value_indices[
                    min_pos + 1 : max_pos + 1
                ]
            elif pos > new_pos:
                # moved left
                self.__value_indices[min_pos + 1 : max_pos + 1] = self.__value_indices[
                    min_pos:max_pos
                ]

            # Update moved value's position
            self.__value_indices[new_pos] = ind

            # Update values position member
            for k, ind in enumerate(self.__value_indices[min_pos : max_pos + 1]):
                self.__values[ind].position = min_pos + k

    def compute_new_pos(self, mixer_value: MixerValue) -> int:
        pos = mixer_value.position

        # Wrap around + handle the weird end/start condition
        new_pos = self.__wrap_pos(pos + mixer_value.value, mod_val=self.__n_numbers - 1)
        if new_pos == 0:
            new_pos = self.__n_numbers - 1
        elif new_pos == self.__n_numbers - 1:
            new_pos = 0
        return new_pos

    def __wrap_pos(self, in_ind: int, mod_val: int) -> int:
        ind = in_ind % mod_val
        if ind < 0:
            ind += self.__n_numbers - 1
        return ind

    def get_grove_coordinates(self):
        starting_pos = [value.position for value in self.__values if value.value == 0][0]

        wrapped_offset_pos = [
            self.__wrap_pos(starting_pos + offset, mod_val=self.__n_numbers)
            for offset in [1000, 2000, 3000]
        ]

        value_inds = [self.__value_indices[pos] for pos in wrapped_offset_pos]
        return [self.__values[ind].value for ind in value_inds]

    # Debug
    def mixed_values(self) -> List[int]:
        return [self.__values[ind].value for ind in self.__value_indices]


######################################
# Solvers
######################################
@utils.timing.timing
def solve_part_1(input_file: str):
    numbers = utils.io.read_file_lines(input_file, parse_as_type=int)
    mixer = Mixer(numbers)
    mixer.mix_once()
    return sum(mixer.get_grove_coordinates())


@utils.timing.timing
def solve_part_2(input_file: str):
    numbers = utils.io.read_file_lines(input_file, parse_as_type=int)
    mixer = Mixer(numbers, decryption_key=811589153)
    mixer.mix(iter=10)
    return sum(mixer.get_grove_coordinates())


if __name__ == "__main__":
    print("Part I")
    print(solve_part_1("input/day20.txt"))

    print("Part II")
    print(solve_part_2("input/day20.txt"))
