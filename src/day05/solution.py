import copy
import re
import textwrap
from collections import deque
from enum import Enum
from typing import List, Tuple

import utils.io


class CraneModel(Enum):
    CrateMover_9000 = 0
    CrateMover_9001 = 1


def parse_input(input_file: str):
    data = utils.io.read_file_lines(input_file)

    stacks = []
    operations = []

    operation_regex = "move (\d+) from (\d+) to (\d+)"

    stacks = None
    for line in data:
        m = re.match(operation_regex, line)
        if m is not None:
            operations.append((int(m.group(1)), int(m.group(2)), int(m.group(3))))
        elif "[" not in line:
            # Can skip as info is redundant
            continue
        else:
            # Split line in groups of 3 chars split by a space
            chunks = textwrap.wrap(line, 4, drop_whitespace=False)
            if stacks is None:
                stacks = [deque() for c in chunks]

            # Fill from left, as we see the top of the stack first
            for stack, chunk in zip(stacks, chunks):
                if not chunk[0:3].isspace():
                    stack.appendleft(chunk[1])

    return stacks, operations


def apply_operations(
    stacks: List[deque], operations: List[Tuple[int, int, int]], crane_model: CraneModel
):
    out_stacks = copy.deepcopy(stacks)
    for op in operations:
        if crane_model == CraneModel.CrateMover_9000:
            for k in range(op[0]):
                out_stacks[op[2] - 1].append(out_stacks[op[1] - 1].pop())
        elif crane_model == CraneModel.CrateMover_9001:
            crates_to_move = [out_stacks[op[1] - 1].pop() for k in range(op[0])]
            [out_stacks[op[2] - 1].append(crate) for crate in crates_to_move[::-1]]
        else:
            raise NotImplementedError()

    return out_stacks


def top_crate_in_stacks(stacks: List[deque]) -> str:
    return "".join([s[-1] for s in stacks])


def solve_part_1(input_file: str) -> int:
    stacks, operations = parse_input(input_file)
    stacks = apply_operations(stacks, operations, CraneModel.CrateMover_9000)
    return top_crate_in_stacks(stacks)


def solve_part_2(input_file: str) -> int:
    stacks, operations = parse_input(input_file)
    stacks = apply_operations(stacks, operations, CraneModel.CrateMover_9001)
    return top_crate_in_stacks(stacks)


if __name__ == "__main__":
    print("Part I")
    print(solve_part_1("input/day5.txt"))

    print("Part II")
    print(solve_part_2("input/day5.txt"))
