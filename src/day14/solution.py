from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple

import numpy as np

import utils
from utils.map import MapExtent, MapLine, MapPosition, MapStructure


@dataclass
class FillingCaveMap:
    structures: List[MapStructure] = field(default_factory=list)
    sand_source_pos: MapPosition = field(default_factory=lambda: MapPosition(500, 0))
    floor_depth_below_scan: int = None

    class SandState(Enum):
        SETTLED = 0
        FALLING_DOWN = 1
        FALLING_INTO_ABYSS = 2
        BLOCKED = 4

    def __post_init__(self) -> None:
        # Determine size of map in memory
        # Consider normal structures
        self.extent: MapExtent = sum([s.extent() for s in self.structures], MapExtent())

        # Make sure we include the source
        self.extent += self.sand_source_pos.extent()

        # Add floor if needed
        if self.floor_depth_below_scan is not None:
            # Infinite plane, but only needs to extent laterally (floor_depth-sand_source.y) + 1
            # to either side of sand_source.x
            floor_depth = self.extent.bottom_right.y + self.floor_depth_below_scan
            delta_y = floor_depth - self.sand_source_pos.y + 1
            floor_start = MapPosition(x=self.sand_source_pos.x - delta_y, y=floor_depth)
            floor_end = MapPosition(x=self.sand_source_pos.x + delta_y, y=floor_depth)
            floor = MapLine([floor_start, floor_end])
            self.structures.append(MapStructure([floor]))

            self.extent += floor

        self.__map_sand_source = self.sand_source_pos - self.extent.top_left
        self.__map_extent = self.extent - self.extent.top_left
        self.__map = np.full((self.extent.height(), self.extent.width()), fill_value=".")
        self.__map_extent = MapExtent.from_shape(self.__map.shape)
        self.__map[self.__map_sand_source.s_] = "+"

        for s in self.structures:
            for line in s.lines:
                map_wall = line - self.extent.top_left
                self.__map[map_wall.s_] = "#"

    def fill_with_sand(self) -> int:
        n_sand_units = 0
        while True:
            sand_state = self.__generate_sand()
            if sand_state == self.SandState.FALLING_DOWN:
                raise RuntimeError("Sand should not be falling at this point")
            if sand_state != self.SandState.FALLING_INTO_ABYSS:
                n_sand_units += 1
            if sand_state in (self.SandState.FALLING_INTO_ABYSS, self.SandState.BLOCKED):
                break
        return n_sand_units

    def __generate_sand(self) -> SandState:
        pos = self.__map_sand_source
        sand_state = self.SandState.FALLING_DOWN
        # Drop until sand settles or falls into abyss
        while pos is not None:
            sand_state, pos = self.__move_sand(pos)

        return sand_state

    def __move_sand(self, pos: MapPosition) -> Tuple[SandState, MapPosition]:
        down = pos + MapPosition(x=0, y=1)
        down_left = pos + MapPosition(x=-1, y=1)
        down_right = pos + MapPosition(x=1, y=1)

        for next_pos in [down, down_left, down_right]:
            if not self.__map_extent.contains(next_pos):
                return self.SandState.FALLING_INTO_ABYSS, None
            if self.__map[next_pos.s_] == ".":
                return self.SandState.FALLING_DOWN, next_pos

        if self.__map[pos.s_] == "+":
            # Cave full
            self.__map[pos.s_] = "O"
            return self.SandState.BLOCKED, None
        else:
            # Sand settles
            self.__map[pos.s_] = "O"
            return self.SandState.SETTLED, None

    # For visualization/debugging
    def __str__(self) -> str:
        return f"top left = ({self.extent.top_left.x}, {self.extent.top_left.y})\n{self.__map}"

    def map(self) -> np.ndarray:
        return self.__map.copy()


####################################
# Parsing helpers
####################################
def parse_data_as_MapStructure(data: utils.io.InputData) -> MapStructure:
    def _parse_point(corner_str: str) -> MapPosition:
        coords = [int(c) for c in corner_str.split(",")]
        if len(coords) != 2:
            raise ValueError("Invalid corner string")
        return MapPosition(x=coords[0], y=coords[1])

    if len(data) < 2:
        raise ValueError("Invalid structure string")

    corners = [_parse_point(corner_str) for corner_str in data]
    walls = [MapLine([c1, c2]) for c1, c2 in zip(corners[:-1], corners[1:])]
    return MapStructure(lines=walls)


def setup_map_structures(input_file: str) -> List[MapStructure]:
    parser = utils.io.FileParser(data_parser=parse_data_as_MapStructure, line_sep=" -> ")
    return parser.parse_file(input_file)


####################################
# Solvers
####################################
@utils.timing.timing
def solve_part_1(input_file: str):
    map_structures = setup_map_structures(input_file)
    cave_map = FillingCaveMap(map_structures)
    n_units = cave_map.fill_with_sand()

    # Visualization
    os.makedirs("output", exist_ok=True)
    np.savetxt("output/day14_part1.txt", cave_map.map(), fmt="%s")
    return n_units


@utils.timing.timing
def solve_part_2(input_file: str):
    map_structures = setup_map_structures(input_file)
    cave_map = FillingCaveMap(map_structures, floor_depth_below_scan=2)
    n_units = cave_map.fill_with_sand()

    # Visualization
    os.makedirs("output", exist_ok=True)
    np.savetxt("output/day14_part2.txt", cave_map.map(), fmt="%s")
    return n_units


if __name__ == "__main__":
    print("Part I")
    print(solve_part_1("input/day14.txt"))

    print("Part II")
    print(solve_part_2("input/day14.txt"))
