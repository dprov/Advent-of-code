from typing import List

import utils.io

VALUE_a = 1
VALUE_A = 27


def get_char_value(c: str):
    if c.islower():
        return ord(c) - ord("a") + VALUE_a
    else:
        return ord(c) - ord("A") + VALUE_A


def pack_priority(pack: List[str]):
    n_items_per_half = len(pack) // 2
    first = pack[:n_items_per_half]
    second = pack[n_items_per_half:]

    common_item = list(set(first).intersection(set(second)))[0]

    return get_char_value(common_item)


def group_packs(packs: List[List[str]], group_size) -> List[List[List[str]]]:
    return zip(*[iter(packs)] * group_size)


def pack_group_priority(pack_group: List[List[str]]):
    group_set = set(pack_group[0])
    for pack in pack_group[1:]:
        group_set = group_set.intersection(set(pack))
    badge = list(group_set)[0]
    return get_char_value(badge)


def solve_part_1(input_file: str) -> int:
    packs = utils.io.read_file_lines(input_file)

    return sum([pack_priority(pack) for pack in packs])


def solve_part_2(input_file: str) -> int:
    packs = utils.io.read_file_lines(input_file)
    pack_groups = group_packs(packs, 3)
    return sum([pack_group_priority(group) for group in pack_groups])


if __name__ == "__main__":
    print("Part I")
    print(solve_part_1("input/day03.txt"))

    print("Part II")
    print(solve_part_2("input/day03.txt"))
