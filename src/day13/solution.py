from __future__ import annotations

import ast
import math
from dataclasses import dataclass
from typing import List, Union

from tribool import Tribool

import utils


@dataclass
class Packet:
    value: Union[List, int]

    # Make instances sortable by defining < and == operators
    def __lt__(self, other) -> bool:
        res = self.__check_order(self, other)
        return res.value is True

    def __eq__(self, other) -> bool:
        res = self.__check_order(self, other)
        return res.value is None

    @staticmethod
    def __check_order(first: Packet, second: Packet) -> Tribool:
        first_is_list = isinstance(first.value, list)
        left_is_list = isinstance(second.value, list)

        # if none are lists
        if not first_is_list and not left_is_list:
            return (
                Tribool(None)
                if first.value == second.value
                else Tribool(first.value < second.value)
            )

        # if both are lists
        elif first_is_list and left_is_list:
            first_length = len(first.value)
            second_length = len(second.value)
            for left_item, right_item in zip(first.value, second.value):
                res = Packet.__check_order(Packet(left_item), Packet(right_item))
                if res.value is not None:
                    return res
            return (
                Tribool(None)
                if first_length == second_length
                else Tribool(first_length < second_length)
            )

        # if only one is list
        elif first_is_list:
            return Packet.__check_order(first, Packet([second.value]))
        else:
            return Packet.__check_order(Packet([first.value]), second)


@dataclass
class PacketPair:
    left: Packet
    right: Packet

    def is_ordered(self) -> bool:
        return self.left < self.right


####################################
# Parsing utils
####################################
def parse_data_as_packet(data: utils.io.InputData) -> Packet:
    return Packet(ast.literal_eval(data))


def parse_data_as_packet_pair(data: utils.io.InputData) -> Packet:
    if len(data) != 2:
        raise ValueError("Inconsistent input")
    # Each input line is basically __repr__(value)
    packets = [Packet(ast.literal_eval(line)) for line in data]
    return PacketPair(left=packets[0], right=packets[1])


####################################
# Solvers
####################################
@utils.timing.timing
def solve_part_1(path: str) -> int:
    parser = utils.io.FileParser(data_parser=parse_data_as_packet_pair, line_group_size=2)
    pairs: List[PacketPair] = parser.parse_file(path)
    are_ordered = [pair.is_ordered() for pair in pairs]

    return sum([ind + 1 for ind, is_ordered in enumerate(are_ordered) if is_ordered])


@utils.timing.timing
def solve_part_2(path: str) -> int:
    parser = utils.io.FileParser(data_parser=parse_data_as_packet)
    packets: List[Packet] = parser.parse_file(path)

    divider_packets = [Packet([[2]]), Packet([[6]])]

    packets.extend(divider_packets)
    sorted_packets = sorted(packets)

    return math.prod([sorted_packets.index(d) + 1 for d in divider_packets])


if __name__ == "__main__":
    print("Part I")
    print(solve_part_1("input/day13.txt"))

    print("Part II")
    print(solve_part_2("input/day13.txt"))
