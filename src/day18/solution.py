from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple

import numpy as np
import scipy.ndimage.measurements
import skimage.segmentation

import utils


######################################
# Geometry utils
######################################
class VoxelFace(Enum):
    X_POS = 1
    X_NEG = 1 << 1

    Y_POS = 1 << 2
    Y_NEG = 1 << 3

    Z_POS = 1 << 4
    Z_NEG = 1 << 5

    ALL = X_POS | X_NEG | Y_POS | Y_NEG | Z_POS | Z_NEG
    NONE = 0

    def inverse(self) -> VoxelFace:
        if self in [self.X_POS, self.Y_POS, self.Z_POS]:
            return VoxelFace(self.value << 1)
        elif self in [self.X_NEG, self.Y_NEG, self.Z_NEG]:
            return VoxelFace(self.value >> 1)
        if self == self.ALL:
            return self.NONE
        else:
            self.ALL

    @staticmethod
    def all_single_faces() -> List[VoxelFace]:
        return [
            VoxelFace.X_POS,
            VoxelFace.X_NEG,
            VoxelFace.Y_POS,
            VoxelFace.Y_NEG,
            VoxelFace.Z_POS,
            VoxelFace.Z_NEG,
        ]


# hashable
@dataclass(frozen=True, eq=True)
class Voxel:
    x: int = 0
    y: int = 0
    z: int = 0

    def __post_init__(self):
        super().__setattr__("s_", np.s_[self.x, self.y, self.z])

    def __add__(self, other) -> Voxel:
        if isinstance(other, Voxel):
            return Voxel(self.x + other.x, self.y + other.y, self.z + other.z)
        elif isinstance(other, VoxelFace):
            if other == VoxelFace.ALL:
                delta_x = 1
                delta_y = 1
                delta_z = 1
            else:
                delta_x = 1 if other == VoxelFace.X_POS else -1 if other == VoxelFace.X_NEG else 0
                delta_y = 1 if other == VoxelFace.Y_POS else -1 if other == VoxelFace.Y_NEG else 0
                delta_z = 1 if other == VoxelFace.Z_POS else -1 if other == VoxelFace.Z_NEG else 0
            return Voxel(self.x + delta_x, self.y + delta_y, self.z + delta_z)
        else:
            raise NotImplementedError()

    def neighbors(self) -> Tuple[Voxel, ...]:
        return tuple([self + face for face in VoxelFace.all_single_faces()])


######################################
# Lava behavior
######################################
@dataclass
class LavaDroplet:
    lava_cubes: List[Voxel]
    # Convenience to keep track of which voxels of array contain lava
    presence_marker = VoxelFace.Z_NEG.value << 1

    def __post_init__(self):
        # Assume array is small and no negative coordinates
        x_max = max([c.x for c in self.lava_cubes])
        y_max = max([c.y for c in self.lava_cubes])
        z_max = max([c.z for c in self.lava_cubes])

        # Each bit of the integer means a surface is an outer surface
        self.__array = np.zeros((x_max + 1, y_max + 1, z_max + 1), dtype=np.uint8)

        for cube in self.lava_cubes:
            self.__set_faces_for_cube(cube)

    def __set_faces_for_cube(self, cube):
        self.__array[cube.s_] = VoxelFace.ALL.value + self.presence_marker
        for face in VoxelFace.all_single_faces():
            neighbor = cube + face
            # If neighbour present, deactivate touching faces
            if self.__is_in_array(neighbor) and self.__array[neighbor.s_] > 0:
                self.__array[cube.s_] &= ~face.value
                self.__array[neighbor.s_] &= ~face.inverse().value

    def contains_lava_array(self) -> np.ndarray:
        return np.greater(self.__array, 0)

    def __is_in_array(self, cube: Voxel):
        x_size, y_size, z_size = self.__array.shape
        return (
            cube.x >= 0
            and cube.x < x_size
            and cube.y >= 0
            and cube.y < y_size
            and cube.z >= 0
            and cube.z < z_size
        )

    def total_surface_area(self) -> int:
        return np.unpackbits(np.bitwise_and(self.__array, VoxelFace.ALL.value)).sum()


######################################
# Parsing helpers
######################################
def parse_data_as_voxel(data: utils.io.InputData) -> Voxel:
    if len(data) != 3:
        raise ValueError("Invalid lava cube position")
    return Voxel(x=int(data[0]), y=int(data[1]), z=int(data[2]))


@utils.timing.timing
def setup_droplet(input_file: str) -> LavaDroplet:
    parser = utils.io.FileParser(data_parser=parse_data_as_voxel, line_sep=",")
    lava_cubes = parser.parse_file(input_file)
    return LavaDroplet(lava_cubes)


######################################
# Solvers
######################################
@utils.timing.timing
def solve_part_1(input_file: str):
    droplet = setup_droplet(input_file)
    return droplet.total_surface_area()


# Equivalent to skimage.segmentation.clear_border with 6 (instead of 14 ) connectivity
# From https://stackoverflow.com/questions/70193514/change-connection-definitions-for-clear-border-in-python
def clear_border_adjacent(matrix):
    border_cleared = skimage.segmentation.clear_border(scipy.ndimage.label(matrix)[0])
    border_cleared[border_cleared > 0] = 1
    return border_cleared


@utils.timing.timing
def solve_part_2(input_file: str):
    droplet = setup_droplet(input_file)
    non_filled = np.logical_not(droplet.contains_lava_array())
    to_fill = clear_border_adjacent(non_filled)

    lava_cubes = list(droplet.lava_cubes)

    x_coords, y_coords, z_coords = np.nonzero(to_fill)
    lava_cubes.extend([Voxel(x, y, z) for x, y, z in zip(x_coords, y_coords, z_coords)])

    filled_droplet = LavaDroplet(lava_cubes)
    return filled_droplet.total_surface_area()


if __name__ == "__main__":
    print("Part I")
    print(solve_part_1("input/day18.txt"))

    print("Part II")
    print(solve_part_2("input/day18.txt"))
