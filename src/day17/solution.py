from __future__ import annotations

import copy
import itertools
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple

import numpy as np

import utils.io

# Notes:
# - Could make some optimizations, such as
#   - forgetting about areas that cannot possibly be filled anymore
#   - Consider that for some shapes, the range of attainable rows might be shorter (e.g. smallest gap at row R is w wide, shape is W > w wide)
# IDEAS:
#   - Have a growing occupancy map + slicing objects (perhaps invert the whole problem top down for simplicity). Each shape has a occupancy matrix. When considering move, check dot product of object and local map occupancy
# - Shapes are just masks. moves sideways/downwards are just shifting the map slice indices. Note that map "walls" are not too tricky, because all masks will behave nicel wrt walls (but not fallen rocks)
# - Since a rock can never stop falling on a sideways move, might as well consider one time step as (move sideways, vertical drop, check if done)
# - Keep Chamber as a list so that it can grow fast. When checking collisions, create np array if it makes things easier
# - Always have a stack of 3 empty rows at the end of the list to accomodate whatever rock


###########################################
#
###########################################


class Direction(Enum):
    LEFT = "<"
    RIGHT = ">"
    DOWN = "v"


@dataclass
class Position:
    x: int
    y: int


class RockShapes(Enum):
    # Getting error about truth value of numpy array when Enum is being parsed
    # DASH = np.ones((1, 4), dtype=bool)
    # PLUS = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=bool)
    # L = np.array([[0, 0, 1], [0, 0, 1], [1, 1, 1]], dtype=bool)
    # I = np.ones((4, 1), dtype=bool)
    # SQUARE = np.ones((2, 2), dtype=bool)

    DASH = [[True, True, True, True]]
    PLUS = [[False, True, False], [True, True, True], [False, True, False]]
    L = [[True, True, True], [False, False, True], [False, False, True]]
    I = [[True], [True], [True], [True]]
    SQUARE = [[True, True], [True, True]]

    def width(self) -> int:
        return len(self.value[0])

    def height(self) -> int:
        return len(self.value)


@dataclass
class Rock:
    position: Position  # Bottom left of encasing rectangle
    shape: RockShapes

    def move(self, direction: Direction):
        if direction == Direction.LEFT:
            self.position.x -= 1
        elif direction == Direction.RIGHT:
            self.position.x += 1
        elif direction == Direction.DOWN:
            self.position.y -= 1
        else:
            raise NotImplementedError()

    def x(self) -> int:
        return self.position.x

    def y(self) -> int:
        return self.position.y


class FallingRockChamber:
    tower_height = 0
    width = 7
    rock_spawn_head_space = 3
    _fill_height: int = 0
    _resting_rocks_count: int = 0

    def __init__(self):
        self._buffer_head_space = self.rock_spawn_head_space + max(
            [shape.height() for shape in RockShapes]
        )
        self._fill_buffer = []

    def _pad_fill_buffer(self) -> None:
        rows_to_pad = max(0, self._buffer_head_space - (len(self._fill_buffer) - self.tower_height))

        for dh in range(rows_to_pad):
            self._fill_buffer.append([False] * self.width)

    def _test_collision(self, rock: Rock) -> bool:
        if rock.x() < 0 or (rock.x() + rock.shape.width() - 1 >= self.width) or rock.y() < 0:
            return True
        surrounding_rows = np.array(
            self._fill_buffer[rock.position.y : rock.position.y + rock.shape.height()]
        )
        rock_surroundings = surrounding_rows[
            :, rock.position.x : rock.position.x + rock.shape.width()
        ]
        return np.any(np.array(rock.shape.value) * rock_surroundings)

    def _test_move(self, rock: Rock, direction: Direction) -> Tuple[bool, Rock]:
        # Check if the original object is
        test_rock = copy.deepcopy(rock)
        test_rock.move(direction)
        if self._test_collision(test_rock):
            return False, rock
        else:
            return True, test_rock

    def _settle_rock(self, rock: Rock) -> None:
        rock_pos = rock.position
        self.tower_height = max(self.tower_height, rock_pos.y + rock.shape.height())
        for ind, row in enumerate(rock.shape.value):
            tmp = self._fill_buffer[rock_pos.y + ind][rock_pos.x : rock_pos.x + rock.shape.width()]
            tmp = [t | r for t, r in zip(tmp, row)]

            # for x, y in zip(tmp, row):
            # x |= y
            self._fill_buffer[rock_pos.y + ind][rock_pos.x : rock_pos.x + rock.shape.width()] = tmp
            # self._fill_buffer[rock_pos.y + ind][rock_pos.x : rock_pos.x + rock.shape.width()] = row

    def fill(self, jet_pattern: List[Direction], n_rocks: int) -> int:
        rock_shapes = itertools.cycle(RockShapes)
        jet_directions = itertools.cycle(jet_pattern)
        for ind in range(n_rocks):
            self._pad_fill_buffer()
            rock = Rock(
                position=Position(2, self.tower_height + self.rock_spawn_head_space),
                shape=next(rock_shapes),
            )
            still_moving = True
            while still_moving:
                # First move sideways
                __, rock = self._test_move(rock, direction=next(jet_directions))
                # Then move downwards
                still_moving, moved_rock = self._test_move(rock, direction=Direction.DOWN)
                # Check if settled
                if still_moving:
                    rock = moved_rock
                else:
                    self._settle_rock(rock)


# Cycle RockShapes, cycle pattern


###########################################
# Parsing utils
###########################################
def parse_data_as_jet_pattern(input_file: str) -> List[Direction]:
    jet_pattern = utils.io.read_file_lines(input_file)[0]
    return [Direction(j) for j in jet_pattern]


###########################################
# Solvers
###########################################
def solve_part_1(input_file: str) -> int:
    jet_pattern = parse_data_as_jet_pattern(
        input_file,
    )
    chamber = FallingRockChamber()
    chamber.fill(jet_pattern=jet_pattern, n_rocks=2022)
    return chamber.tower_height


def solve_part_2(input_file: str) -> int:
    jet_pattern = parse_data_as_jet_pattern(input_file)
    return None


if __name__ == "__main__":
    print("Part I")
    # print(solve_part_1("example_input/day17.txt"))
    print(solve_part_1("input/day17.txt"))

    print("Part II")
    print(solve_part_2("input/day17.txt"))
