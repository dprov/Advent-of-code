from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import List, Sequence, Type

import sympy

import utils


# Utilities related to prime number factorization
def get_prime_factors(x):
    return set(sympy.primefactors(x, limit=19))


# From https://stackoverflow.com/a/39106237
def find_primes_up_to(n):
    out = list()
    sieve = [True] * (n + 1)
    for p in range(2, n + 1):
        if sieve[p] and sieve[p] % 2 == 1:
            out.append(p)
            for i in range(p, n + 1, p):
                sieve[i] = False
    return out


# Classes for items in monkey game
class FactorizedInt:
    max_divisor: int = None
    track_value = True
    # Idea: Track list of prime divisors + remainder for each prime
    def __init__(self, value: int) -> None:
        self.value = value if self.track_value else None
        prime_divisors = set(find_primes_up_to(self.max_divisor))
        self.remainders = {prime: value % prime for prime in prime_divisors}

    def __mul__(self, value) -> FactorizedInt:
        # out = copy.deepcopy(self) # slow
        out = self
        if self.track_value:
            out.value *= value
        for prime, remainder in out.remainders.items():
            out.remainders[prime] = (remainder * value) % prime
        return out

    def __add__(self, value) -> FactorizedInt:
        # out = copy.deepcopy(self)  # slow
        out = self
        if self.track_value:
            out.value += value
        for prime, remainder in out.remainders.items():
            out.remainders[prime] = (remainder + value) % prime
        return out

    def __pow__(self, value) -> FactorizedInt:
        # out = copy.deepcopy(self)  # slow
        out = self
        if self.track_value:
            out.value = out.value**value
        for prime, remainder in out.remainders.items():
            if remainder > 0:
                out.remainders[prime] = (remainder**value) % prime
        return out

    def __floordiv__(self, value) -> FactorizedInt:
        if not self.track_value:
            raise NotImplementedError()
        out = type(self)(self.value // value)
        return out

    def is_divisible_by(self, value) -> bool:
        value_factors = get_prime_factors(value)
        for factor in value_factors:
            if self.remainders[factor] > 0:
                return False
        return True


@dataclass
class ThrownItem:
    item: FactorizedInt
    recipient: int


# Classes for defining callbacks for all the monkey/game steps
@dataclass
class Callback:
    def _callback(self):
        raise NotImplementedError()

    def apply(self, item: FactorizedInt):
        return self._callback(item)


class OperationCallback(Callback):
    class Operator(Enum):
        ADD = "+"
        MUL = "*"
        POW = "**"

    def __init__(self, operator: OperationCallback.Operator, arg: int) -> None:
        self.__arg = arg

        if operator == OperationCallback.Operator.ADD:
            self.__callback_fun = self.__callback_add
        elif operator == OperationCallback.Operator.MUL:
            self.__callback_fun = self.__callback_mul
        elif operator == OperationCallback.Operator.POW:
            self.__callback_fun = self.__callback_pow

    def __callback_add(self, item: FactorizedInt) -> FactorizedInt:
        return item + self.__arg

    def __callback_mul(self, item: FactorizedInt) -> FactorizedInt:
        return item * self.__arg

    def __callback_pow(self, item: FactorizedInt) -> FactorizedInt:
        return item**self.__arg

    # @utils.timing.timing
    def _callback(self, item: FactorizedInt) -> FactorizedInt:
        return self.__callback_fun(item)


class TestDivisibilityCallback(Callback):
    def __init__(self, divisor: int, monkey_true: int, monkey_false: int) -> None:
        self.divisor = divisor
        self.monkey_true = monkey_true
        self.monkey_false = monkey_false

    def _callback(self, item: FactorizedInt) -> ThrownItem:
        return ThrownItem(
            item=item,
            recipient=self.monkey_true if item.is_divisible_by(self.divisor) else self.monkey_false,
        )


@dataclass
class WhenBoredCallback(Callback):
    relief_factor: int

    # @utils.timing.timing
    def _callback(self, item: FactorizedInt) -> FactorizedInt:
        if self.relief_factor != 1:
            return item // self.relief_factor
        else:
            return item


# Class for monkey behavior during game
class Monkey:
    def __init__(
        self,
        id: int,
        operation: OperationCallback,
        test: TestDivisibilityCallback,
        starting_values: Sequence[int],
    ) -> None:
        self.id = id
        self.operation = operation
        self.test = test
        self.__starting_item_values = starting_values

        # Game specific
        self.__n_inspected_items: int = 0
        self.__items = None
        self.when_bored = None

    def prepare_for_new_game(self, item_type: Type, when_bored: WhenBoredCallback):
        self.when_bored = when_bored
        self.__n_inspected_items: int = 0
        self.__items = deque([item_type(value) for value in self.__starting_item_values])

    def catch_item(self, item: FactorizedInt) -> None:
        self.__items.append(item)

    def inspect_item(self) -> ThrownItem:
        if not self.__items:
            return None

        self.__n_inspected_items += 1
        item = self.__items.popleft()
        item = self.operation.apply(item)
        item = self.when_bored.apply(item)
        return self.test.apply(item)

    def has_items(self) -> bool:
        return len(self.__items) > 0

    def get_items(self):
        return self.__items

    def count_inspected_items(self) -> int:
        return self.__n_inspected_items


# Class for running game
@dataclass
class MonkeyGame:
    monkeys: List[Monkey]

    @utils.timing.timing
    def play(self, n_rounds: int, when_bored: WhenBoredCallback) -> List[int]:
        max_test_divisor = max([monkey.test.divisor for monkey in self.monkeys])
        item_type = type(
            f"ItemWorry_{max_test_divisor}_{when_bored.relief_factor}",
            (FactorizedInt,),
            {"max_divisor": max_test_divisor, "track_value": when_bored.relief_factor > 1},
        )

        for monkey in self.monkeys:
            monkey.prepare_for_new_game(item_type=item_type, when_bored=when_bored)

        for round in range(n_rounds):
            for monkey in self.monkeys:
                while monkey.has_items():
                    thrown_item = monkey.inspect_item()
                    if thrown_item is not None:
                        self.__throw_item(thrown_item)
        return self.score()

    def score(self):
        monkey_scores = [m.count_inspected_items() for m in self.monkeys]
        sorted_scores = sorted(monkey_scores, reverse=True)
        return sorted_scores[0] * sorted_scores[1]

    def __throw_item(self, thrown_item: ThrownItem) -> None:
        if thrown_item is not None:
            self.monkeys[thrown_item.recipient].catch_item(thrown_item.item)


# Helper for parsing
@dataclass
class MonkeyParser(utils.io.ParserClass):
    @staticmethod
    def line_group_size() -> int:
        return 6

    def parse(self) -> Monkey:
        if len(self.data) != self.line_group_size():
            raise ValueError()

        # Line 0: Monkey declaration
        monkey_id = self.__parse_monkey_id(self.data[0])

        # Line 1: Starting items
        starting_values = self.__parse_starting_values(self.data[1])

        # Line 2: Operation
        operation = self.__parse_operation(self.data[2])

        # Lines 3-5: Test
        test = self.__parse_test(
            divisor_str=self.data[3], if_true_str=self.data[4], if_false_str=self.data[5]
        )

        # Line 6 should be empty

        return Monkey(id=monkey_id, starting_values=starting_values, operation=operation, test=test)

    def __parse_monkey_id(self, monkey_id_str) -> int:
        monkey_id_str = self.__check_line(monkey_id_str, "Monkey ")
        return int(monkey_id_str[0])

    def __parse_starting_values(self, starting_values_str) -> List[int]:
        starting_values_str = self.__check_line(self.data[1], "  Starting items: ")
        return [int(value) for value in starting_values_str.split(", ")]

    def __parse_operation(self, operation_str: str) -> OperationCallback:
        operation_str = self.__check_line(operation_str, "  Operation: new = ")
        # Assume format is old op val, where op is one of OperationCallback.Operator and val is int or old
        remaining_str = self.__check_line(operation_str, "old ")
        if remaining_str == "* old":
            operator = OperationCallback.Operator.POW
            arg = 2
        else:
            operator = OperationCallback.Operator(remaining_str[0])

            # Skip operator and space
            remaining_str = remaining_str[2:]
            arg = int(remaining_str)
        return OperationCallback(operator=operator, arg=arg)

    def __parse_test(
        self, divisor_str: str, if_true_str: str, if_false_str: str
    ) -> TestDivisibilityCallback:
        divisor = int(self.__check_line(divisor_str, "  Test: divisible by "))
        monkey_if_true = int(self.__check_line(if_true_str, "    If true: throw to monkey "))
        monkey_if_false = int(self.__check_line(if_false_str, "    If false: throw to monkey "))
        return TestDivisibilityCallback(
            divisor=divisor, monkey_true=monkey_if_true, monkey_false=monkey_if_false
        )

    def __check_line(self, line: str, line_start: str) -> str:
        if line[: len(line_start)] != line_start:
            raise ValueError(f"Expected line '{line}' to start with '{line_start}'")
        return line[len(line_start) :]


if __name__ == "__main__":
    monkeys: List[Monkey] = utils.io.parse_file_as_type("input/day11", MonkeyParser)
    game = MonkeyGame(monkeys=monkeys)
    print("Part I")
    print(game.play(n_rounds=20, when_bored=WhenBoredCallback(relief_factor=3)))

    print("Part II")
    print(game.play(n_rounds=10000, when_bored=WhenBoredCallback(relief_factor=1)))
