from __future__ import annotations

import multiprocessing
from dataclasses import dataclass, field
from typing import List

import portion as P

import utils
from utils.map import ManhattanDistance, MapPosition


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


class SensorReadingParser(utils.io.ParserClass):
    @staticmethod
    def line_regex() -> str:
        number = "[-\d]"
        return f"[\w ]+ x=({number}+), y=({number}+): [\w ]+ x=({number}+), y=({number}+)"

    def parse(self) -> SensorReading:
        if len(self.data) < 4:
            raise ValueError("Invalid sensor reading string")

        sensor_pos = MapPosition(int(self.data[0]), int(self.data[1]))
        beacon_pos = MapPosition(int(self.data[2]), int(self.data[3]))
        return SensorReading(sensor=sensor_pos, beacon=beacon_pos)


def get_sensor_coverage(sensor_readings: SensorReadings, row: int) -> P.Interval:
    no_beacon_interval = sensor_readings.row_coverage(row)

    # Remove beacons from row coverage
    beacons_in_coverage = [
        reading.beacon for reading in sensor_readings.readings if reading.beacon.y == row
    ]
    for beacon in beacons_in_coverage:
        no_beacon_interval &= ~P.open(beacon.x - 1, beacon.x + 1)

    return no_beacon_interval


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
    sensor_readings = utils.io.parse_file_as_type(input_file, SensorReadingParser)
    sensor_readings = SensorReadings(sensor_readings)
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
    sensor_readings = utils.io.parse_file_as_type(input_file, SensorReadingParser)
    sensor_readings = SensorReadings(sensor_readings)

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
