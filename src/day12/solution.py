from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

import dijkstar
import dijkstar.algorithm
import numpy as np

import utils
from utils.map import MapExtent, MapLine, MapPosition, MapStructure

######################################
# Graph setup and solving
######################################


@utils.timing.timing
def setup_graph(topo_map: np.ndarray, reversed=False) -> dijkstar.Graph:
    if reversed:
        is_reachable = lambda h, h_neighbor: h - h_neighbor <= 1
    else:
        is_reachable = lambda h, h_neighbor: h_neighbor - h <= 1

    graph = dijkstar.Graph()
    for r, row in enumerate(topo_map):
        for c, node_height in enumerate(row):
            node = MapPosition(c, r)
            for n in node.neighbors(MapExtent.from_shape(topo_map.shape)):
                if is_reachable(h=node_height, h_neighbor=topo_map[n.s_]):
                    graph.add_edge(node, n, 1)
    return graph


@utils.timing.timing
def find_shortest_path_length(topo_map, start_pos, end_pos):
    graph = setup_graph(topo_map)
    path = dijkstar.find_path(
        graph,
        start_pos,
        end_pos,
        # Change to A*. For size of map, it's longer...
        # heuristic_func=lambda n1, n2, e1, e2: abs(n2.x - n1.x) + abs(n2.y - n1.y),
    )
    return path.total_cost


@utils.timing.timing
def find_shortest_path_length_from_lowest_elevation(topo_map, end_pos):
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
        start_pos = MapPosition(start[1], start[0])
        try:
            path = dijkstar.algorithm.extract_shortest_path_from_predecessor_list(
                predecessors, d=start_pos
            )
            if shortest_path_length is None or path.total_cost < shortest_path_length:
                shortest_path_length = path.total_cost
        except:
            pass
    return shortest_path_length


######################################
# Parsing helpers
######################################
def extract_start_end_pos(
    topo_map: np.ndarray, start_marker="S", end_marker="E"
) -> Tuple[MapPosition, MapPosition]:
    start = np.argwhere(topo_map == start_marker).squeeze()
    end = np.argwhere(topo_map == end_marker).squeeze()

    if start.size != 2 or end.size != 2:
        raise ValueError()

    start_pos = MapPosition(start[1], start[0])
    end_pos = MapPosition(end[1], end[0])

    topo_map[start_pos.s_] = "a"
    topo_map[end_pos.s_] = "z"

    return (start_pos, end_pos)


@utils.timing.timing
def parse_data_as_map_data(path: str) -> Tuple[np.ndarray, MapPosition, MapPosition]:
    topo_map = utils.io.read_file_as_array(path, dtype="<U1")

    start_pos, end_pos = extract_start_end_pos(topo_map)

    topo_map = utils.conversions.alpha_array_to_int(topo_map)
    return topo_map, start_pos, end_pos


######################################
# Solvers
######################################
def solve_part_1(input_file: str) -> int:
    topo_map, start_pos, end_pos = parse_data_as_map_data(input_file)
    return find_shortest_path_length(topo_map, start_pos, end_pos)


def solve_part_2(input_file: str) -> int:
    topo_map, __, end_pos = parse_data_as_map_data(input_file)
    return find_shortest_path_length_from_lowest_elevation(topo_map, end_pos)


if __name__ == "__main__":
    print("Part I")
    print(solve_part_1("input/day12.txt"))

    print("Part II")
    print(solve_part_2("input/day12.txt"))
