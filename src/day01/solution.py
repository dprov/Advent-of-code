from typing import List, Union

import utils.io

InputDataList = List[Union[str, List[str]]]


def parse_input(input_file: str) -> List[int]:
    calories_str = utils.io.read_file_lines(input_file)

    calories_str.append("")
    elf_start_ind = 0
    calories_per_elf = []
    for ind, c_str in enumerate(calories_str):
        if c_str == "":
            if ind > elf_start_ind:
                calories_per_elf.append(
                    sum([int(c_str) for c_str in calories_str[elf_start_ind:ind]])
                )
            elf_start_ind = ind + 1
    return calories_per_elf


def solve_part_1(input_file: str) -> int:
    calories_per_elf = parse_input(input_file)
    return max(calories_per_elf)


def solve_part_2(input_file: str) -> int:
    calories_per_elf = parse_input(input_file)
    return sum(sorted(calories_per_elf, reverse=True)[0:3])


if __name__ == "__main__":
    print("Part I")
    print(solve_part_1("input/day01.txt"))

    print("Part II")
    print(solve_part_2("input/day01.txt"))
