from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Set

import utils.io

###############################################
# Classes for representing rope position/motion
###############################################


# Helper for parsing
class Direction(Enum):
    Up = "U"
    Down = "D"
    Left = "L"
    Right = "R"


@dataclass(frozen=True, eq=True)
class Position:
    # immutable, with equality test operator to make it hashable
    x: int = 0
    y: int = 0


@dataclass
class Move:
    direction: Direction
    distance: int

    def apply(self, pos: Position) -> Position:
        x = pos.x
        y = pos.y
        if self.direction == Direction.Up:
            y += self.distance
        elif self.direction == Direction.Down:
            y -= self.distance
        elif self.direction == Direction.Left:
            x -= self.distance
        elif self.direction == Direction.Right:
            x += self.distance
        else:
            raise NotImplementedError()
        return Position(x, y)


class RopeTracker:
    def __init__(self, start_pos=Position(), n_knots: int = 2) -> None:
        if n_knots < 2:
            raise ValueError("Rope too short")
        self.__head = start_pos
        self.__tail = [start_pos] * (n_knots - 1)

        self.__visited_by_tail_end: Set[Position] = {start_pos}

    def move(self, moves: Move):
        for move in moves:
            # break down head moves into unit moves
            unit_head_move = Move(direction=move.direction, distance=1)
            for k in range(move.distance):
                self.__head = unit_head_move.apply(self.__head)
                self.__update_tail_pos()
                self.__visited_by_tail_end.add(self.__tail[-1])

    def __update_tail_pos(self):
        def need_to_move(dist_dir: bool, dist_perp: bool) -> bool:
            return dist_dir > 1 or (abs(dist_perp) > 1 and dist_dir > 0)

        lead = self.__head
        for ind, follower in enumerate(self.__tail):
            dist_up = lead.y - follower.y
            dist_right = lead.x - follower.x

            move_up = need_to_move(dist_up, dist_right)
            move_down = need_to_move(-dist_up, dist_right)
            move_right = need_to_move(dist_right, dist_up)
            move_left = need_to_move(-dist_right, dist_up)

            new_x = follower.x + int(move_right) - int(move_left)
            new_y = follower.y + int(move_up) - int(move_down)
            self.__tail[ind] = Position(new_x, new_y)
            lead = self.__tail[ind]

    def n_visited_by_tail(self) -> int:
        return len(self.__visited_by_tail_end)


# Functions for solving
def parse_input(path: str) -> List[Move]:
    moves = utils.io.read_file_lines(path)

    return [Move(direction=Direction(move[0]), distance=int(move[2:])) for move in moves]


def count_visited_by_tail(rope: RopeTracker, moves: List[Move]) -> int:
    rope.move(moves)
    return rope.n_visited_by_tail()


def solve_part_1(input_file: str) -> int:
    moves = parse_input(input_file)
    return count_visited_by_tail(rope=RopeTracker(n_knots=2), moves=moves)


def solve_part_2(input_file: str) -> int:
    moves = parse_input(input_file)
    return count_visited_by_tail(rope=RopeTracker(n_knots=10), moves=moves)


if __name__ == "__main__":
    print("Part I")
    print(solve_part_1("input/day09.txt"))

    print("Part II")
    print(solve_part_2("input/day09.txt"))
