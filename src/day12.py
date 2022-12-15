from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import dijkstar
import dijkstar.algorithm
import numpy as np

import utils


# Position needs to be hashable
@dataclass(frozen=True, eq=True)
class Position:
    row: int
    col: int

    def __post_init__(self):
        # Trick to set member despite class being frozen
        super().__setattr__("s_", np.s_[self.row, self.col])

    def neighbors(self, map_size: Tuple(int, int)) -> List[Position]:
        neighbors = [
            self + delta
            for delta in [Position(-1, 0), Position(1, 0), Position(0, -1), Position(0, 1)]
        ]
        neighbors = [n for n in neighbors if n.is_inside(map_size)]
        return neighbors

    def __add__(self, other: Position) -> Position:
        return Position(self.row + other.row, self.col + other.col)

    def is_inside(self, map_size: Tuple(int, int)) -> bool:
        return self.row >= 0 and self.row < map_size[0] and self.col >= 0 and self.col < map_size[1]


@utils.timing.timing
def setup_graph(topo_map: np.ndarray, reversed=False) -> dijkstar.Graph:
    if reversed:
        is_reachable = lambda h, h_neighbor: h - h_neighbor <= 1
    else:
        is_reachable = lambda h, h_neighbor: h_neighbor - h <= 1

    graph = dijkstar.Graph()
    for r, row in enumerate(topo_map):
        for c, node_height in enumerate(row):
            node = Position(r, c)
            for n in node.neighbors(map_size=topo_map.shape):
                if is_reachable(h=node_height, h_neighbor=topo_map[n.s_]):
                    graph.add_edge(node, n, 1)
    return graph


@utils.timing.timing
def solve_part_1(topo_map, start_pos, end_pos):
    graph = setup_graph(topo_map)
    path = dijkstar.find_path(
        graph,
        start_pos,
        end_pos,
        # Change to A*. For size of map, it's longer...
        heuristic_func=lambda n1, n2, e1, e2: abs(n2.row - n1.row) + abs(n2.col - n1.col),
    )
    print(path.total_cost)
    return path.total_cost


@utils.timing.timing
def solve_part_2(topo_map, end_pos):
    # 2 ways:
    # Brute force:
    # - Call find_path for each starting position and keep shortest path
    # Better way: Use reversed graph and loop over start positions "later" (20x faster on input)
    # - Build reversed graph (source= end, dest=start)
    # - Build predecessor map (for each node, what was the previous node if we started from source. No notion of destination)
    # - For each suitable destination, find path from source to destination. Keep shortest path

    reversed_graph = setup_graph(topo_map, reversed=True)
    predecessors = dijkstar.algorithm.single_source_shortest_paths(
        reversed_graph,
        s=end_pos,
    )
    starts = np.argwhere(topo_map == 0).squeeze()
    shortest_path_length = None
    for start in starts:
        start_pos = Position(start[0], start[1])
        try:
            path = dijkstar.algorithm.extract_shortest_path_from_predecessor_list(
                predecessors, d=start_pos
            )
            if shortest_path_length is None or path.total_cost < shortest_path_length:
                shortest_path_length = path.total_cost
        except:
            pass
    return shortest_path_length


# Parsing utils
def extract_start_end_pos(
    topo_map: np.ndarray, start_marker="S", end_marker="E"
) -> Tuple[Position, Position]:
    start = np.argwhere(topo_map == start_marker).squeeze()
    end = np.argwhere(topo_map == end_marker).squeeze()

    if start.size != 2 or end.size != 2:
        raise ValueError()

    start_pos = Position(start[0], start[1])
    end_pos = Position(end[0], end[1])

    topo_map[start_pos.s_] = "a"
    topo_map[end_pos.s_] = "z"

    return (start_pos, end_pos)


@utils.timing.timing
def parse_input(path: str) -> Tuple[np.ndarray, Position, Position]:
    topo_map = utils.io.read_file_as_array(path, dtype="<U1")

    start_pos, end_pos = extract_start_end_pos(topo_map)

    topo_map = utils.conversions.alpha_array_to_int(topo_map)
    return topo_map, start_pos, end_pos


if __name__ == "__main__":
    topo_map, start_pos, end_pos = parse_input("input/day12")

    print("Part I")
    print(solve_part_1(topo_map, start_pos, end_pos))

    print("Part II")
    print(solve_part_2(topo_map, end_pos))
