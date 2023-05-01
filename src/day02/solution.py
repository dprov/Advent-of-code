from enum import Enum
from typing import Callable

import utils.io


class Pick(Enum):
    Rock = 1
    Paper = 2
    Scissor = 3


class Outcome(Enum):
    Lose = 0
    Draw = 3
    Win = 6


their_pick_map = {"A": Pick.Rock, "B": Pick.Paper, "C": Pick.Scissor}
my_pick_map_pt1 = {"X": Pick.Rock, "Y": Pick.Paper, "Z": Pick.Scissor}
outcome_map_pt2 = {"X": Outcome.Lose, "Y": Outcome.Draw, "Z": Outcome.Win}


def play_round_part_1(input_1: str, input_2: str) -> int:
    their_pick = their_pick_map[input_1]
    my_pick = my_pick_map_pt1[input_2]

    is_win = my_pick.value == (their_pick.value % len(Pick)) + 1
    is_draw = my_pick.value == their_pick.value
    outcome = Outcome.Win if is_win else Outcome.Draw if is_draw else Outcome.Lose

    return outcome.value + my_pick.value


def play_round_part_2(input_1: str, input_2: str) -> int:
    their_pick = their_pick_map[input_1]
    outcome = outcome_map_pt2[input_2]
    if outcome == Outcome.Win:
        my_pick = Pick((their_pick.value % len(Pick)) + 1)
    elif outcome == Outcome.Draw:
        my_pick = their_pick
    else:
        my_pick = Pick((their_pick.value - 2) % len(Pick) + 1)
    return outcome.value + my_pick.value


def play(input_file, round_solver: Callable[[str, str], int]):
    rounds = utils.io.read_file_lines(input_file)
    total_score = 0
    for round in rounds:
        inputs = round.split(" ")
        total_score += round_solver(inputs[0], inputs[1])
    return total_score


def solve_part_1(input_file: str) -> int:
    return play(input_file, play_round_part_1)


def solve_part_2(input_file: str) -> int:
    return play(input_file, play_round_part_2)


if __name__ == "__main__":
    print("Part I")
    print(solve_part_1("input/day02.txt"))

    print("Part II")
    print(solve_part_2("input/day02.txt"))
