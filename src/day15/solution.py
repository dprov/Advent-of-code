from __future__ import annotations

import multiprocessing
from dataclasses import dataclass, field
from typing import List

import portion as P

import utils
from utils.map import ManhattanDistance, MapPosition


####################################
# Sensors
####################################
@dataclass
class SensorReading:
    sensor: utils.map.MapPosition
    beacon: utils.map.MapPosition

    def __post_init__(self):
        self.__beacon_dist = utils.map.ManhattanDistance.between(self.sensor, self.beacon)

    def sensing_range(self) -> ManhattanDistance:
        return self.__beacon_dist

    def row_coverage(self, row: int) -> P.Interval:
        one_sided_extent = self.sensing_range().distance - abs(self.sensor.y - row)
        return P.closed(self.sensor.x - one_sided_extent, self.sensor.x + one_sided_extent)


@dataclass
class SensorReadings:
    readings: List[SensorReading] = field(default_factory=list)

    def row_coverage(self, row: int) -> P.Interval:
        interval = P.empty()
        for reading in self.readings:
            interval |= reading.row_coverage(row)
        return interval


####################################
# Parsing helpers
####################################
number_regex = "[-\d]"
sensor_reading_regex = (
    f"[\w ]+ x=({number_regex}+), y=({number_regex}+): [\w ]+ x=({number_regex}+),"
    f" y=({number_regex}+)"
)


def parse_data_as_SensorReading(data: utils.io.InputData) -> SensorReading:
    if len(data) < 4:
        raise ValueError("Invalid sensor reading string")

    sensor_pos = MapPosition(int(data[0]), int(data[1]))
    beacon_pos = MapPosition(int(data[2]), int(data[3]))
    return SensorReading(sensor=sensor_pos, beacon=beacon_pos)


def setup_sensor_readings(input_file: str) -> SensorReadings:
    parser = utils.io.FileParser(
        data_parser=parse_data_as_SensorReading, line_regex=sensor_reading_regex
    )
    sensor_reading_list = parser.parse_file(input_file)
    return SensorReadings(sensor_reading_list)


####################################
# Solvers
####################################
def count_no_beacon_positions(sensor_readings: SensorReadings, row: int) -> int:
    no_beacon_interval = sensor_readings.row_coverage(row)

    # Remove beacons from row coverage
    beacons_in_coverage = [
        reading.beacon for reading in sensor_readings.readings if reading.beacon.y == row
    ]
    for beacon in beacons_in_coverage:
        no_beacon_interval &= ~P.open(beacon.x - 1, beacon.x + 1)

    # Sum length of each atomic subinterval
    return sum([i.upper - i.lower + 1 for i in no_beacon_interval])


@utils.timing.timing
def solve_part_1(input_file: str, row: int = 2000000) -> int:
    sensor_readings = setup_sensor_readings(input_file)
    return count_no_beacon_positions(sensor_readings, row)


# Pool.map only works with pickleable functions. AFAIK, it only works with "top-level" functions, so
# I used global parameters /variables. I don't care enough to make it cleaner for now.
max_coord_val = 0
frequency_multiplier = 4000000
sensor_readings = None


def check_row(row):
    x_interval = P.closed(0, max_coord_val)
    covered_interval = sensor_readings.row_coverage(row)
    if x_interval not in covered_interval:
        covered_interval = (covered_interval | ~x_interval) & x_interval

        x = x_interval - covered_interval
        x = x.upper - 1
        return frequency_multiplier * x + row
    else:
        return None


@utils.timing.timing
def solve_part_2(input_file: str, grid_size: int = 4000000) -> int:
    global sensor_readings
    global max_coord_val
    max_coord_val = grid_size
    sensor_readings = setup_sensor_readings(input_file)

    with multiprocessing.Pool(8) as pool:
        for result in pool.map(check_row, range(max_coord_val + 1)):
            if result is not None:
                print(result)
                return result

    return None


if __name__ == "__main__":
    print("Part I")
    print(solve_part_1("input/day15.txt"))

    print("Part II")
    print(solve_part_2("input/day15.txt"))
