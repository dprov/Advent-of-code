from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

import numpy as np


# Hashable
@dataclass(frozen=True, eq=True, order=True)
class MapPosition:
    x: int = 0
    y: int = 0

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

    def extent(self) -> MapExtent:
        return MapExtent([self])

    def neighbors(self, map_extent: MapExtent) -> List[MapPosition]:
        neighbors = [
            self + delta
            for delta in [
                MapPosition(-1, 0),
                MapPosition(1, 0),
                MapPosition(0, -1),
                MapPosition(0, 1),
            ]
        ]
        neighbors = [n for n in neighbors if map_extent.contains(n)]
        return neighbors


@dataclass(frozen=True, eq=True, order=True)
class ManhattanDistance:
    distance: int = 0

    @staticmethod
    def __between_points(p1: MapPosition, p2: MapPosition) -> int:
        return abs(p2.x - p1.x) + abs(p2.y - p1.y)

    @classmethod
    def between(cls, p1: MapPosition, p2: MapPosition) -> ManhattanDistance:
        return ManhattanDistance(cls.__between_points(p1, p2))

    def __add__(self, other) -> ManhattanDistance:
        if isinstance(other, int):
            return ManhattanDistance(self.distance + other)
        elif isinstance(other, ManhattanDistance):
            return ManhattanDistance(self.distance + other.distance)
        else:
            raise NotImplementedError()

    def __sub__(self, other) -> ManhattanDistance:
        if isinstance(other, int):
            return ManhattanDistance(self.distance - other)
        elif isinstance(other, ManhattanDistance):
            return ManhattanDistance(self.distance - other.distance)
        else:
            raise NotImplementedError()


# Hashable
@dataclass(frozen=True, eq=True)
class MapExtent:
    _positions: List[MapPosition] = field(default_factory=list)

    def __post_init__(self):
        positions = [p for p in self._positions if p is not None]
        if positions:
            sorted_x = sorted([p.x for p in positions])
            sorted_y = sorted([p.y for p in positions])
            super().__setattr__("top_left", MapPosition(x=sorted_x[0], y=sorted_y[0]))
            super().__setattr__("bottom_right", MapPosition(x=sorted_x[-1], y=sorted_y[-1]))
            super().__setattr__(
                "s_", np.s_[sorted_y[0] : sorted_y[-1] + 1, sorted_x[0] : sorted_x[-1] + 1]
            )
        else:
            super().__setattr__("top_left", None)
            super().__setattr__("bottom_right", None)
            super().__setattr__("s_", np.s_[0:0, 0:0])

    @classmethod
    def from_shape(cls, shape: Tuple[int, int]) -> MapExtent:
        return cls([MapPosition(0, 0), MapPosition(shape[1] - 1, shape[0] - 1)])

    def width(self) -> int:
        return self.bottom_right.x - self.top_left.x + 1

    def height(self) -> int:
        return self.bottom_right.y - self.top_left.y + 1

    def __add__(self, other) -> MapExtent:
        if isinstance(other, MapPosition):
            positions = [self.top_left + other, self.bottom_right + other]
            return MapExtent(positions)

        if isinstance(other, MapExtent):
            positions = [self.top_left, self.bottom_right, other.top_left, other.bottom_right]
            return MapExtent(positions)

        else:
            raise NotImplementedError()

    def __sub__(self, other) -> MapExtent:
        if isinstance(other, MapPosition):
            positions = [self.top_left - other, self.bottom_right - other]
            return MapExtent(positions)
        else:
            raise NotImplementedError()

    def contains(self, other) -> bool:
        if isinstance(other, MapPosition):
            return (
                other.x >= self.top_left.x
                and other.x <= self.bottom_right.x
                and other.y >= self.top_left.y
                and other.y <= self.bottom_right.y
            )
        elif isinstance(other, MapExtent):
            return (
                other.top_left.x >= self.top_left.x
                and other.bottom_right.x <= self.bottom_right.x
                and other.top_left.y >= self.top_left.y
                and other.bottom_right.y <= self.bottom_right.y
            )
        elif isinstance(other, MapStructure):
            return self.contains(other.extent())
        else:
            return NotImplementedError()


# Hashable
@dataclass(frozen=True, eq=True)
class MapLine(MapExtent):
    def __post_init__(self):
        super().__post_init__()
        if (self.top_left.x - self.bottom_right.x > 0) and (
            self.top_left.y - self.bottom_right.y > 0
        ):
            raise ValueError("Line must be horizontal or vertical")

    def __add__(self, other) -> MapExtent:
        return super().__add__(other)

    def length(self) -> ManhattanDistance:
        return ManhattanDistance.between(self.top_left, self.bottom_right)


# Hashable
@dataclass(frozen=True, eq=True)
class MapStructure:
    lines: List[MapLine] = field(default_factory=list)

    def extent(self) -> MapExtent:
        return sum(self.lines, MapExtent())
