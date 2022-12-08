import re

from interval import Interval

pair_regex = "(\d+)\-(\d+)\,(\d+)\-(\d+)"

if __name__ == "__main__":
    with open("input/day4") as f:
        data = f.read()
        pairs = data.split("\n")

        matches = [re.match(pair_regex, pair) for pair in pairs]
        first_intervals = [Interval(int(m.group(1)), int(m.group(2))) for m in matches]
        second_intervals = [Interval(int(m.group(3)), int(m.group(4))) for m in matches]

        pair_has_full_overlap = [
            (f in s) or (s in f) for (f, s) in zip(first_intervals, second_intervals)
        ]
        n_full_overlaps = sum(pair_has_full_overlap)

        pair_has_partial_overlap = [
            f.overlaps(s) for (f, s) in zip(first_intervals, second_intervals)
        ]

        n_partial_overlaps = sum(pair_has_partial_overlap)

        print("Part I")
        print(n_full_overlaps)

        print("Part II")
        print(n_partial_overlaps)
