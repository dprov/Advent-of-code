value_a = 1
value_A = 27


def get_char_value(c: str):
    if c.islower():
        return ord(c) - ord("a") + value_a
    else:
        return ord(c) - ord("A") + value_A


if __name__ == "__main__":
    with open("input/day3") as f:
        data = f.read()
        packs = data.split("\n")

        sum_of_priorities_pt1 = 0
        for pack in packs:
            n_items_per_half = len(pack) // 2
            first = pack[:n_items_per_half]
            second = pack[n_items_per_half:]

            common_item = list(set(first).intersection(set(second)))[0]

            sum_of_priorities_pt1 += get_char_value(common_item)

        pack_groups = zip(*[iter(packs)] * 3)
        sum_of_priorities_pt2 = 0
        for group in pack_groups:
            badge = list(set(group[0]).intersection(set(group[1])).intersection(set(group[2])))[0]
            sum_of_priorities_pt2 += get_char_value(badge)

    print("Part I")
    print(sum_of_priorities_pt1)

    print("Part II")
    print(sum_of_priorities_pt2)
