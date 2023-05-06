from __future__ import annotations

import itertools
from dataclasses import dataclass
from enum import Enum
from typing import Any

import utils.io

###########################################
# Define number system
###########################################
MAX_DIGITS = 25
POWERS_OF_5 = [5**ind for ind in range(20)]
MAX_VAL_FOR_SNAFU_NB_DIGITS = list(itertools.accumulate([2 * p for p in POWERS_OF_5]))


@dataclass
class SnafuDigitValue:
    integer: int
    string: str


class SnafuDigit(Enum):
    MINUS_TWO = "="
    MINUS_ONE = "-"
    ZERO = "0"
    ONE = "1"
    TWO = "2"

    def string(self) -> str:
        return self.value

    def integer(self) -> int:
        if self == SnafuDigit.MINUS_TWO:
            return -2
        if self == SnafuDigit.MINUS_ONE:
            return -1
        if self == SnafuDigit.ZERO:
            return 0
        if self == SnafuDigit.ONE:
            return 1
        if self == SnafuDigit.TWO:
            return 2
        return NotImplementedError()

    def invert(self) -> SnafuDigit:
        if self == SnafuDigit.MINUS_TWO:
            return SnafuDigit.TWO
        if self == SnafuDigit.MINUS_ONE:
            return SnafuDigit.ONE
        if self == SnafuDigit.ZERO:
            return SnafuDigit.ZERO
        if self == SnafuDigit.ONE:
            return SnafuDigit.MINUS_ONE
        if self == SnafuDigit.TWO:
            return SnafuDigit.MINUS_TWO
        return NotImplementedError()


snafu_digit_str_to_int = {"=": -2, "-": -1, "0": 0, "1": 1, "2": 2}


@dataclass
class SnafuNumber:
    value: int

    @classmethod
    def from_string(cls, snafu_str: str) -> SnafuNumber:
        digits = [snafu_digit_str_to_int[chr] for chr in snafu_str]

        value = 0
        for ind, digit in enumerate(digits[::-1]):
            value += 5**ind * digit
        return cls(value)

    def to_string(self) -> str:
        # Convert the absolute value, then invert if needed
        abs_val = abs(self.value)
        n_digits = next(
            ind + 1 for ind, x in enumerate(MAX_VAL_FOR_SNAFU_NB_DIGITS) if x >= abs_val
        )
        string = ""
        remainder = abs_val
        # Unit place is index 0
        for place in range(n_digits)[::-1]:
            abs_remainder = abs(remainder)

            next_digit_max_val = 0 if place == 0 else MAX_VAL_FOR_SNAFU_NB_DIGITS[place - 1]

            if abs_remainder <= next_digit_max_val:
                digit = SnafuDigit.ZERO
            elif abs_remainder > next_digit_max_val + POWERS_OF_5[place]:
                digit = SnafuDigit.TWO
            else:
                digit = SnafuDigit.ONE

            # Now consider number polarity
            if remainder < 0:
                digit = digit.invert()

            remainder -= digit.integer() * POWERS_OF_5[place]
            string += digit.string()

        if remainder != 0:
            raise RuntimeError()
        return string

    def __add__(self, other) -> SnafuNumber:
        return SnafuNumber(self.value + other.value)


###########################################
# Parsing utils
###########################################
def parse_data_as_snafu_numbers(input_file: str):
    numbers = utils.io.read_file_lines(input_file, parse_as_type=SnafuNumber.from_string)
    return numbers


###########################################
# Solvers
###########################################
def solve_part_1(input_file: str) -> int:
    numbers = parse_data_as_snafu_numbers(input_file)
    snafu_sum = SnafuNumber(sum([n.value for n in numbers]))
    return snafu_sum.to_string()


def solve_part_2(input_file: str) -> int:
    numbers = utils.io.read_file_lines(input_file, parse_as_type=SnafuNumber.from_string)
    return None


if __name__ == "__main__":
    print("Part I")
    print(solve_part_1("input/day25.txt"))

    print("Part II")
    print(solve_part_2("input/day25.txt"))
