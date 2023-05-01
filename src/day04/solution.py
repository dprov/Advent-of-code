import re
from typing import Callable, List

from interval import Interval

import utils.io

PAIR_REGEX = "(\d+)\-(\d+)\,(\d+)\-(\d+)"


def parse_input_to_intervals(input_file: str):
    pairs = utils.io.read_file_lines(input_file)

    matches = [re.match(PAIR_REGEX, pair) for pair in pairs]
    first_intervals = [Interval(int(m.group(1)), int(m.group(2))) for m in matches]
    second_intervals = [Interval(int(m.group(3)), int(m.group(4))) for m in matches]
    return first_intervals, second_intervals


def check_intervals(
    intervals_1: List[Interval],
    intervals_2: List[Interval],
    predicate: Callable[[Interval, Interval], bool],
) -> List[bool]:
    return [predicate(f, s) for (f, s) in zip(intervals_1, intervals_2)]


def count_full_overlapping_pairs(intervals_1: List[Interval], intervals_2: List[Interval]) -> int:
    have_full_overlap = check_intervals(intervals_1, intervals_2, lambda x, y: (x in y) or (y in x))
    return sum(have_full_overlap)


def count_partial_overlapping_pairs(
    intervals_1: List[Interval], intervals_2: List[Interval]
) -> int:
    have_partial_overlap = check_intervals(intervals_1, intervals_2, lambda x, y: x.overlaps(y))
    return sum(have_partial_overlap)


def solve_part_1(input_file: str) -> int:
    first_elf_intervals, second_elf_intervals = parse_input_to_intervals(input_file)
    return count_full_overlapping_pairs(first_elf_intervals, second_elf_intervals)


def solve_part_2(input_file: str) -> int:
    first_elf_intervals, second_elf_intervals = parse_input_to_intervals(input_file)
    return count_partial_overlapping_pairs(first_elf_intervals, second_elf_intervals)


if __name__ == "__main__":
    print("Part I")
    print(solve_part_1("input/day04.txt"))

    print("Part II")
    print(solve_part_2("input/day04.txt"))
