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


@utils.timing.timing
def solve_part_1(sensor_readings: SensorReadings, row: int):
    no_beacon_interval = sensor_readings.row_coverage(row)

    # Remove beacons from row coverage
    beacons_in_coverage = [
        reading.beacon for reading in sensor_readings.readings if reading.beacon.y == row
    ]
    for beacon in beacons_in_coverage:
        no_beacon_interval &= ~P.open(beacon.x - 1, beacon.x + 1)

    # Sum length of each atomic subinterval
    return sum([i.upper - i.lower + 1 for i in no_beacon_interval])


PART_2_MAX_COORD = 4000000


def check_row(row):
    x_interval = P.closed(0, PART_2_MAX_COORD)
    covered_interval = sensor_readings.row_coverage(row)
    if x_interval not in covered_interval:
        covered_interval = (covered_interval | ~x_interval) & x_interval

        x = x_interval - covered_interval
        x = x.upper - 1
        return PART_2_MAX_COORD * x + row
    else:
        return None


@utils.timing.timing
def solve_part_2_v2(max_coord: int) -> int:
    with multiprocessing.Pool(8) as pool:
        for result in pool.map(check_row, range(max_coord + 1)):
            if result is not None:
                return result
    return None


if __name__ == "__main__":
    sensor_readings = utils.io.parse_file_as_type("input/day15", SensorReadingParser)

    sensor_readings = SensorReadings(sensor_readings)

    print("Part I")
    print(solve_part_1(sensor_readings, 2000000))

    print("Part II")
    print(solve_part_2_v2(sensor_readings, PART_2_MAX_COORD))
