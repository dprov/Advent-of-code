from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import List

import utils


class BinaryOperator(Enum):
    ADD = "+"
    SUB = "-"
    MUL = "*"
    DIV = "/"
    EQ = "=="

    def apply(self, arg1: int, arg2: int) -> int:
        if self == BinaryOperator.ADD:
            return int(arg1 + arg2)
        elif self == BinaryOperator.SUB:
            return int(arg1 - arg2)
        elif self == BinaryOperator.MUL:
            return int(arg1 * arg2)
        elif self == BinaryOperator.DIV:
            return int(arg1 // arg2)
        elif self == BinaryOperator.EQ:
            return int(arg1 == arg2)
        else:
            raise NotImplementedError()

    def invert(self, result: int, arg1: int = None, arg2: int = None) -> int:
        arg1_provided = arg1 is not None
        arg = arg1 if arg1_provided else arg2

        if self == BinaryOperator.ADD:
            return int(result - arg)
        elif self == BinaryOperator.SUB:
            return int(arg - result if arg1_provided else result + arg)
        elif self == BinaryOperator.MUL:
            return int(result // arg)
        elif self == BinaryOperator.DIV:
            return int(arg // result if arg1_provided else result * arg)
        elif self == BinaryOperator.EQ:
            return arg if result else None
        else:
            raise NotImplementedError()


# Classes for each type of monkey
class YellingMonkey:
    @dataclass
    class MonkeyInfo:
        name: str
        value: int = None

    def __init__(self, name: str, number=None) -> None:
        self._info = self.MonkeyInfo(name, number)

    def is_ready(self) -> bool:
        return True

    def hear(self, monkeys: List[YellingMonkey], reverse_order=False):
        pass

    def shout(self, reverse_order=False) -> MonkeyInfo:
        return self._info

    def name(self) -> str:
        return self._info.name


class MathYellingMonkey(YellingMonkey):
    def __init__(
        self, name: str, operator: BinaryOperator, monkey_1_name: str, monkey_2_name: str
    ) -> None:
        self.operator = operator
        self.monkey_1_info = self.MonkeyInfo(monkey_1_name, None)
        self.monkey_2_info = self.MonkeyInfo(monkey_2_name, None)
        self._solved_monkey_info = None

        super().__init__(name=name)

    def is_ready(self) -> bool:
        # Both inputs and output are available
        return None not in [self._info.value, self.monkey_1_info.value, self.monkey_2_info.value]

    def __try_to_solve(self):
        # If we now have both inputs available
        if None not in [self.monkey_1_info.value, self.monkey_2_info.value]:
            self._info.value = self.operator.apply(
                self.monkey_1_info.value, self.monkey_2_info.value
            )

        # If only one input is missing and we have the solution
        if self._info.value is not None and (
            (self.monkey_1_info.value is None) ^ (self.monkey_2_info.value is None)
        ):
            solved_monkey_val = self.operator.invert(
                self._info.value, self.monkey_1_info.value, self.monkey_2_info.value
            )

            if self.monkey_1_info.value is None:
                self.monkey_1_info.value = solved_monkey_val
                self._solved_monkey_info = self.monkey_1_info
            else:
                self.monkey_2_info.value = solved_monkey_val
                self._solved_monkey_info = self.monkey_2_info

    def hear(self, monkeys: List[YellingMonkey], reverse_order=False):
        if not self.is_ready():
            # Includes self in case order is reversed
            names_of_missing_monkeys = [
                self.name(),
                self.monkey_1_info.name,
                self.monkey_2_info.name,
            ]
            monkey_infos = [monkey.shout(reverse_order=reverse_order) for monkey in monkeys]
            missing_monkey_infos = [
                info for info in monkey_infos if info.name in names_of_missing_monkeys
            ]

            for monkey_info in missing_monkey_infos:
                if monkey_info.name == self.name():
                    self._info = monkey_info
                elif monkey_info.name == self.monkey_1_info.name:
                    self.monkey_1_info = monkey_info
                else:
                    self.monkey_2_info = monkey_info

            self.__try_to_solve()

    def shout(self, reverse_order=False) -> YellingMonkey.MonkeyInfo:
        if reverse_order:
            if self._solved_monkey_info is not None:
                return self._solved_monkey_info
            elif self.monkey_1_info.value is not None:
                return self.monkey_1_info
            else:
                return self.monkey_2_info
        else:
            return self._info


class RootMonkey(MathYellingMonkey):
    def __init__(self, name: str, monkey_1_name: str, monkey_2_name: str) -> None:
        super().__init__(
            name=name,
            operator=BinaryOperator.EQ,
            monkey_1_name=monkey_1_name,
            monkey_2_name=monkey_2_name,
        )
        self._info.value = 1


class Human(YellingMonkey):
    def __init__(self, name: str) -> None:
        super().__init__(name=name)

    def is_ready(self) -> bool:
        return self._info.value is not None

    def hear(self, monkeys: List[YellingMonkey], reverse_order=False):
        if not self.is_ready():
            for monkey in monkeys:
                monkey_info = monkey.shout(reverse_order=reverse_order)
                if monkey_info.name == self.name():
                    self._info.value = monkey_info.value
                    break


class MonkeyParser(utils.io.ParserClass):
    @staticmethod
    def line_split() -> str:
        return ": "

    def parse(self):
        name = self.data[0]
        m = re.match("(\w{4}) ([+\-*/]) (\w{4})", self.data[1])
        if m is not None:
            return MathYellingMonkey(
                name=name,
                operator=BinaryOperator(m.group(2)),
                monkey_1_name=m.group(1),
                monkey_2_name=m.group(3),
            )
        else:
            return YellingMonkey(name=name, number=int(self.data[1]))


def shout_it_all_out(monkeys: List[YellingMonkey], reverse_order=False) -> YellingMonkey:
    root_monkey = [monkey for monkey in monkeys if monkey.name() == "root"][0]

    # Make monkeys shout until no new information is available
    remaining_monkeys = monkeys
    n_new_ready_monkeys = 1  # Arbitrary non-zero starting value
    while n_new_ready_monkeys > 0:
        shouting_monkeys = [monkey for monkey in remaining_monkeys if monkey.is_ready()]
        remaining_monkeys = [monkey for monkey in remaining_monkeys if not monkey.is_ready()]

        for monkey in remaining_monkeys:
            monkey.hear(shouting_monkeys, reverse_order=reverse_order)
        n_new_ready_monkeys = len(shouting_monkeys)

    return root_monkey


@utils.timing.timing
def solve_part_1(input_file: str) -> int:
    monkeys: List[YellingMonkey] = utils.io.parse_file_as_type(input_file, MonkeyParser)
    root_monkey = shout_it_all_out(monkeys)
    return root_monkey.shout().value


@utils.timing.timing
def solve_part_2(input_file: str) -> int:
    monkeys: List[YellingMonkey] = utils.io.parse_file_as_type(input_file, MonkeyParser)
    # Modify root monkey rules
    root_ind = [ind for ind, monkey in enumerate(monkeys) if monkey.name() == "root"][0]
    monkeys[root_ind] = RootMonkey(
        name=monkeys[root_ind].name(),
        monkey_1_name=monkeys[root_ind].monkey_1_info.name,
        monkey_2_name=monkeys[root_ind].monkey_2_info.name,
    )

    # Modify human rules
    human_ind = [ind for ind, monkey in enumerate(monkeys) if monkey.name() == "humn"][0]
    monkeys[human_ind] = Human(name=monkeys[human_ind].name())

    # Solve as much of the monkeys as possible
    shout_it_all_out(monkeys)

    # (Optional) At this point, we can remove all monkeys that have been heard. Make sure to keep root
    remaining_monkeys = [
        monkey for monkey in monkeys if (not monkey.is_ready()) or (monkey.name() == "root")
    ]
    shout_it_all_out(remaining_monkeys, reverse_order=True)

    human = [monkey for monkey in remaining_monkeys if isinstance(monkey, Human)][0]
    return human.shout().value


if __name__ == "__main__":
    print("Part I")
    print(solve_part_1("input/day21.txt"))

    print("Part II")
    print(solve_part_2("input/day21.txt"))
