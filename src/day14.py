from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple

import numpy as np

import utils


@dataclass(frozen=True, eq=True, order=True)
class MapPosition:
    x: int
    y: int

    def __post_init__(self):
        # Trick to set member despite class being frozen
        super().__setattr__("s_", np.s_[self.y, self.x])

    def __add__(self, other) -> MapPosition:
        if isinstance(other, MapPosition):
            return MapPosition(self.x + other.x, self.y + other.y)
        else:
            raise NotImplementedError()

    def __sub__(self, other) -> MapPosition:
        if isinstance(other, MapPosition):
            return MapPosition(self.x - other.x, self.y - other.y)
        else:
            raise NotImplementedError()

    def is_inside(self, map_size: Tuple[int, int]) -> bool:
        return self.x >= 0 and self.x < map_size[1] and self.y >= 0 and self.y < map_size[0]


@dataclass(frozen=True, eq=True, order=True)
class MapLine:
    start: MapPosition
    end: MapPosition

    def __post_init__(self):
        sorted_x = sorted([self.start.x, self.end.x])
        sorted_y = sorted([self.start.y, self.end.y])
        super().__setattr__("__top_left", MapPosition(x=sorted_x[0], y=sorted_y[0]))
        super().__setattr__("__bottom_right", MapPosition(x=sorted_x[1], y=sorted_y[1]))
        super().__setattr__(
            "s_",
            np.s_[sorted_y[0] : sorted_y[1] + 1, sorted_x[0] : sorted_x[1] + 1],
        )

    def __add__(self, other) -> MapLine:
        if isinstance(other, MapPosition):
            return MapLine(self.start + other, self.end + other)
        else:
            raise NotImplementedError()

    def __sub__(self, other) -> MapLine:
        if isinstance(other, MapPosition):
            return MapLine(self.start - other, self.end - other)
        else:
            raise NotImplementedError()

    def extent(self) -> Tuple[MapPosition, MapPosition]:
        return self.__getattribute__("__top_left"), self.__getattribute__("__bottom_right")


@dataclass
class MapStructure:
    lines: List[MapLine] = field(default_factory=list)

    def extent(self) -> Tuple[MapPosition, MapPosition]:
        x = []
        y = []
        for line in self.lines:
            top_left, bottom_right = line.extent()
            x.extend([top_left.x, bottom_right.x])
            y.extend([top_left.y, bottom_right.y])

        return MapPosition(x=min(x), y=min(y)), MapPosition(x=max(x), y=max(y))


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
        # Make sure we include the source
        top_lefts = [self.sand_source_pos]
        bottom_rights = [self.sand_source_pos]

        # Consider normal structures
        extents = [s.extent() for s in self.structures]
        top_lefts.extend([e[0] for e in extents])
        bottom_rights.extend([e[1] for e in extents])

        # Add floor if needed
        if self.floor_depth_below_scan is not None:
            # Infinite plane, but only needs to extent laterally (floor_depth-sand_source.y) + 1
            # to either side of sand_source.x
            floor_depth = max(bottom_rights, key=lambda p: p.y).y + self.floor_depth_below_scan
            delta_y = floor_depth - self.sand_source_pos.y + 1
            floor_start = MapPosition(x=self.sand_source_pos.x - delta_y, y=floor_depth)
            floor_end = MapPosition(x=self.sand_source_pos.x + delta_y, y=floor_depth)
            floor_structure = MapStructure([MapLine(floor_start, floor_end)])
            self.structures.append(floor_structure)
            top_lefts.append(floor_start)
            bottom_rights.append(floor_end)

        min_x = min(top_lefts, key=lambda p: p.x).x
        min_y = min(top_lefts, key=lambda p: p.y).y

        max_x = max(bottom_rights, key=lambda p: p.x).x
        max_y = max(bottom_rights, key=lambda p: p.y).y

        self.__map_top_left = MapPosition(x=min_x, y=min_y)
        self.__map_sand_source = self.sand_source_pos - self.__map_top_left
        self.__map = np.full((max_y - min_y + 1, max_x - min_x + 1), fill_value=".")
        self.__map[self.__map_sand_source.s_] = "+"

        for s in self.structures:
            for line in s.lines:
                map_wall = line - self.__map_top_left
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
            if not next_pos.is_inside(self.__map.shape):
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
        return f"top left = ({self.__map_top_left.x}, {self.__map_top_left.y})\n{self.__map}"

    def map(self) -> np.ndarray:
        return self.__map.copy()


class MapStructureParser(utils.io.ParserClass):
    @staticmethod
    def line_split() -> str:
        # input for str.split() applied to each line. None = no split
        return " -> "

    def parse(self) -> MapStructure:
        if len(self.data) < 2:
            raise ValueError("Invalid structure string")

        corners = [self.__parse_point(corner_str) for corner_str in self.data]
        walls = [MapLine(c1, c2) for c1, c2 in zip(corners[:-1], corners[1:])]
        return MapStructure(lines=walls)

    def __parse_point(self, corner_str: str) -> MapPosition:
        coords = [int(c) for c in corner_str.split(",")]
        if len(coords) != 2:
            raise ValueError("Invalid corner string")
        return MapPosition(x=coords[0], y=coords[1])


@utils.timing.timing
def solve_part_1(structures: List[MapStructure]):
    cave_map = FillingCaveMap(structures)
    n_units = cave_map.fill_with_sand()

    # Visualization
    os.makedirs("output", exist_ok=True)
    np.savetxt("output/day14_part1.txt", cave_map.map(), fmt="%s")
    return n_units


@utils.timing.timing
def solve_part_2(map_structures: List[MapStructure]):
    cave_map = FillingCaveMap(map_structures, floor_depth_below_scan=2)
    n_units = cave_map.fill_with_sand()

    # Visualization
    os.makedirs("output", exist_ok=True)
    np.savetxt("output/day14_part2.txt", cave_map.map(), fmt="%s")
    return n_units


if __name__ == "__main__":
    map_structures = utils.io.parse_file_as_type("input/day14", MapStructureParser)

    print("Part I")
    print(solve_part_1(map_structures))

    print("Part II")
    print(solve_part_2(map_structures))
