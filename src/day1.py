import utils.io


def parse_input(input_file: str):
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


if __name__ == "__main__":
    calories_per_elf = parse_input("input/day1")

    print("Part I")
    print(max(calories_per_elf))

    print("Part II")
    print(sum(sorted(calories_per_elf, reverse=True)[0:3]))
