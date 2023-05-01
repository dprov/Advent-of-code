from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import dijkstar
import dijkstar.algorithm

import utils


# Hashable
@dataclass(frozen=True, eq=True)
class Valve:
    name: str
    flow_rate: int
    tunnels: Tuple[str]

    def __post_init__(self):
        super().__setattr__("tunnels", tuple(self.tunnels))
        # Make hashing quicker
        super().__setattr__("_hash", hash((self.name, self.flow_rate, tuple(self.tunnels))))

    def __hash__(self) -> int:
        return self._hash


class ValveParser(utils.io.ParserClass):
    @staticmethod
    def line_regex() -> str:
        return "Valve (\w{2}) [\w ]+=(\d+); [\w ]+ valves? ([\w, ]+)"

    def parse(self) -> Valve:
        if len(self.data) != 3:
            raise ValueError("Invalid valve string")

        name = self.data[0]
        flow_rate = int(self.data[1])
        tunnels = tuple(self.data[2].split(", "))

        return Valve(name=name, flow_rate=flow_rate, tunnels=tunnels)


ValveTuple = Tuple[Valve, ...]
ValveTupleDict = Dict[ValveTuple, int]
ValveTupleTupleDict = Dict[Tuple[ValveTuple, ...], int]


# Create tuple of sorted valve names for using as key in dictionary
def sort_valve_names(valves: List[Valve]) -> Tuple[Valve, ...]:
    return tuple(sorted([v.name for v in valves]))


# Find quickest travel time between every pair of valves
@utils.timing.timing
def find_travel_times(valves: List[Valve]) -> ValveTupleDict:
    tunnels_graph = dijkstar.Graph()

    valves_dict = {v.name: v for v in valves}

    for v in valves:
        for neighbor_name in v.tunnels:
            neighbor = valves_dict.get(neighbor_name, None)
            if neighbor is not None:
                tunnels_graph.add_edge(v, neighbor, 1)

    travel_times = {}
    for source in valves:
        predecessors = dijkstar.algorithm.single_source_shortest_paths(
            tunnels_graph,
            s=source,
        )
        for destination in valves:
            if destination == source:
                continue
            valve_pair = sort_valve_names((source, destination))
            if valve_pair in travel_times:
                continue

            path = dijkstar.algorithm.extract_shortest_path_from_predecessor_list(
                predecessors, d=destination
            )
            travel_times[valve_pair] = path.total_cost
    return travel_times


def explore_DFS(
    path: Tuple[Valve, ...],
    remaining_valves: List[Valve],
    travel_times: ValveTupleDict,
    remaining_time: int,
    total_flow: int,
    path_flows: ValveTupleDict,
):
    current_flow = total_flow
    for ind, curr_valve in enumerate(remaining_valves):
        valve_pair = sort_valve_names((path[-1], curr_valve))
        current_remaining_time = (
            remaining_time - travel_times[valve_pair] - 1
        )  # include time to open valve

        # The slowest part is due to creating a new tuple every time, then hashing
        valves_in_path = path + (curr_valve,)
        # Skip if already visited, or if valve cannot be open/doesn't have time to have effect
        if valves_in_path in path_flows or current_remaining_time <= 0:
            continue
        current_flow = total_flow + current_remaining_time * curr_valve.flow_rate

        explore_DFS(
            path + (curr_valve,),
            remaining_valves[:ind] + remaining_valves[ind + 1 :],
            travel_times,
            current_remaining_time,
            current_flow,
            path_flows,
        )
        path_flows[valves_in_path] = current_flow


@utils.timing.timing
def solve_part_1(input_file: str) -> int:
    valves = utils.io.parse_file_as_type(input_file, ValveParser)
    travel_times = find_travel_times(valves)
    starting_valve_name = "AA"

    path_start = tuple([v for v in valves if v.name == starting_valve_name])
    remaining_valves = [v for v in valves if v.flow_rate > 0 and v.name != starting_valve_name]

    path_flows = {}
    explore_DFS(
        path=path_start,
        remaining_valves=remaining_valves,
        travel_times=travel_times,
        remaining_time=30,
        total_flow=0,
        path_flows=path_flows,
    )
    max_flow = path_flows[max(path_flows, key=path_flows.get)]
    return max_flow


@utils.timing.timing
def solve_part_2(input_file: str) -> int:
    valves = utils.io.parse_file_as_type(input_file, ValveParser)
    travel_times = find_travel_times(valves)
    starting_valve_name = "AA"

    path_start = tuple(v for v in valves if v.name == starting_valve_name)
    remaining_valves = [v for v in valves if v.flow_rate > 0 and v.name != starting_valve_name]

    path_flows = {}
    explore_DFS(
        path=path_start,
        remaining_valves=remaining_valves,
        travel_times=travel_times,
        remaining_time=26,
        total_flow=0,
        path_flows=path_flows,
    )

    # Need to find the 2 non-overlapping paths that yield maximum results
    # This would be extremely long, but by considering the longest paths first and
    # stopping search when remaining paths are too short to yield the best results, it's very quick
    max_pressure = 0
    sorted_path_info = [
        (k, v) for k, v in sorted(path_flows.items(), reverse=True, key=lambda item: item[1])
    ]

    for ind_1, (path_1, flow_1) in enumerate(sorted_path_info[:-1]):
        next_best_flow = sorted_path_info[ind_1 + 1][1]
        if flow_1 + next_best_flow <= max_pressure:
            break

        for path_2, flow_2 in sorted_path_info[ind_1:]:
            pressure = flow_1 + flow_2
            if pressure <= max_pressure:
                # path_1 cannot beat the max pressure
                break
            if all(v not in path_1[1:] for v in path_2[1:]):
                max_pressure = pressure
                # All remaining path_2 will yield lower pressure
                break

    return max_pressure


if __name__ == "__main__":
    print("Part I")
    print(solve_part_1("input/day16.txt"))

    print("Part II")
    print(solve_part_2("input/day16.txt"))
