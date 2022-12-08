from dataclasses import dataclass
from enum import Enum
from itertools import cycle


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


def score_round_pt1(their_pick: Pick, my_pick: Pick):
    is_win = my_pick.value == (their_pick.value % len(Pick)) + 1
    is_draw = my_pick.value == their_pick.value
    outcome = Outcome.Win if is_win else Outcome.Draw if is_draw else Outcome.Lose

    return outcome.value + my_pick.value


def score_round_pt2(their_pick: Pick, outcome: Outcome):
    if outcome == Outcome.Win:
        my_pick = Pick((their_pick.value % len(Pick)) + 1)
    elif outcome == Outcome.Draw:
        my_pick = their_pick
    else:
        my_pick = Pick((their_pick.value - 2) % len(Pick) + 1)
    return outcome.value + my_pick.value


if __name__ == "__main__":
    with open("input/day2") as f:
        data = f.read()
        rps_rounds = data.split("\n")
        total_score_pt1 = 0
        total_score_pt2 = 0
        for round in rps_rounds:
            inputs = round.split(" ")
            their_pick = their_pick_map[inputs[0]]

            my_pick_pt1 = my_pick_map_pt1[inputs[1]]
            total_score_pt1 += score_round_pt1(their_pick, my_pick_pt1)

            outcome_pt2 = outcome_map_pt2[inputs[1]]
            total_score_pt2 += score_round_pt2(their_pick, outcome_pt2)

        print("Part I")
        print(total_score_pt1)

        print("Part II")
        print(total_score_pt2)
