from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List

import utils.io


# Operation definitions
class OpType(Enum):
    NOOP = "noop"
    ADDX = "addx"


@dataclass
class Operation:
    def __init__(self, cycles_left: int = 0, callback: Callable = None) -> None:
        self.__cycles_left = cycles_left
        self.callback = callback

    def is_done(self) -> bool:
        return self.__cycles_left == 0

    def tick(self) -> bool:
        if not self.is_done():
            self.__cycles_left -= 1
            if self.is_done():
                self._apply()
                return True
        return False

    def _apply(self):
        if self.callback is not None:
            self.callback()


class NoopOperation(Operation):
    def __init__(self) -> None:
        super().__init__(cycles_left=1)


class AddxOperation(Operation):
    def __init__(self, value) -> None:
        self.value = value
        super().__init__(cycles_left=2)

    def _apply(self):
        if self.callback is not None:
            self.callback(self.value)


# Helper for parsing
@dataclass
class OperationParser(utils.io.ParserClass):
    def parse(self):
        op_type = OpType(self.data[0])
        if op_type == OpType.NOOP:
            return NoopOperation()
        elif op_type == OpType.ADDX:
            return AddxOperation(int(self.data[1]))

    @staticmethod
    def line_split() -> str:
        return " "


class CRT:
    set_value: str = "#"
    unset_value: str = "."

    def __init__(self, row_length: int = 40, sprite_half_width: int = 1) -> None:
        self.row_Length = row_length
        self.sprite_half_width = sprite_half_width
        self.__display: List[List[str]] = [[]]

    def __curr_line(self) -> List[int]:
        return self.__display[-1]

    def __curr_line_pixel_ind(self) -> int:
        return len(self.__curr_line())

    def __create_new_line_if_needed(self):
        if len(self.__display[-1]) == self.row_Length:
            self.__display.append([])

    def __get_sprite_positions(self, sprite_pos: int) -> List[int]:
        return range(sprite_pos - self.sprite_half_width, sprite_pos + self.sprite_half_width + 1)

    def __draw_pixel(self, sprite_pos: int):
        self.__create_new_line_if_needed()
        if self.__curr_line_pixel_ind() in self.__get_sprite_positions(sprite_pos):
            self.__curr_line().append(self.set_value)
        else:
            self.__curr_line().append(self.unset_value)

    def draw(self, sprite_pos: int) -> bool:
        self.__draw_pixel(sprite_pos)

    def to_image(self) -> List[str]:
        image = []
        for line in self.__display:
            image.append("".join(line))
        return image


class Processor:
    __X: int = 1
    __signal_strengths: List[int] = field(default_factory=list)

    def __init__(self, crt_row_length: int = 40, sprite_half_width: int = 1) -> None:
        self.__X: int = 1
        self.__signal_strengths: List[int] = []
        self.__crt = CRT(row_length=crt_row_length, sprite_half_width=sprite_half_width)

    def cycle(self):
        return len(self.__signal_strengths)

    def apply_operations(self, ops: List[Operation]):
        for op in ops:
            if isinstance(op, AddxOperation):
                op.callback = self.__incr_X
            while not op.is_done():
                self.__crt.draw(self.__X)
                self.__signal_strengths.append(self.__X * (self.cycle() + 1))
                op.tick()

    def signal_strength(self, cycle: int) -> int:
        return self.__signal_strengths[cycle - 1]

    def __incr_X(self, val):
        self.__X += val

    def get_display_image(self) -> List[str]:
        return self.__crt.to_image()


def get_signal_strengths(processor: Processor, cycle_inds: List[int]) -> int:
    return sum([processor.signal_strength(c) for c in cycle_inds])


def solve_part_1(input_file: str) -> int:
    operations = utils.io.parse_file_as_type(input_file, OperationParser)

    processor = Processor()
    processor.apply_operations(operations)
    return get_signal_strengths(processor=processor, cycle_inds=range(20, processor.cycle(), 40))


def solve_part_2(input_file: str) -> int:
    operations = utils.io.parse_file_as_type(input_file, OperationParser)

    processor = Processor()
    processor.apply_operations(operations)
    return processor.get_display_image()


if __name__ == "__main__":
    print("Part I")
    print(solve_part_1("input/day10.txt"))

    print("Part II")
    a = solve_part_2("input/day10.txt")
    print(*solve_part_2("input/day10.txt"), sep="\n")
