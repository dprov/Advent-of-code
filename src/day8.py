from dataclasses import dataclass
from enum import Enum
from typing import Callable, List

import numpy as np
from numpy.lib.index_tricks import IndexExpression

import utils.io


# Utils for applying 1D processing function along multiple directions on a 2D array
@dataclass
class ArrayView1D:
    # dimension/axis along which to process
    axis: int
    # Slice object for indexing, in order to create view into array (no copy)
    # To be applied to input and output arrays
    s_: IndexExpression = np.s_[:, :]

    def apply_func(self, func: Callable, array: np.ndarray):
        return np.apply_along_axis(func, self.axis, array[self.s_])[self.s_]


def apply_func_along_views(
    func: Callable, array: np.ndarray, views: List[ArrayView1D], aggregate_func: Callable
):
    if not views:
        raise ValueError("No directions to apply")

    result = views[0].apply_func(func, array)

    for view in views[1:]:
        result = aggregate_func(result, view.apply_func(func, array))

    return result


# 1D processing functions
def is_visible_1D(line_of_trees):
    is_visible = np.zeros(line_of_trees.shape, dtype=bool)

    # First tree is visible
    is_visible[0] = True
    highest_tree = line_of_trees[0]
    for ind, tree in enumerate(line_of_trees):
        if tree > highest_tree:
            is_visible[ind] = True
            highest_tree = tree

    return is_visible


def n_trees_in_view_1D(line_of_trees):
    trees_in_view = np.zeros(line_of_trees.shape, dtype=int)

    # First tree cannot see any tree
    n_visible_per_height = np.zeros((10,), dtype=int)
    for ind, tree in enumerate(line_of_trees):
        trees_in_view[ind] += n_visible_per_height[tree]

        # Any trees smaller or equal can now only see this tree
        n_visible_per_height[0 : tree + 1] = 1

        # Taller trees see one more tree
        if tree < 9:
            n_visible_per_height[tree + 1 :] += 1

    return trees_in_view


# Functions for solving
class Direction(Enum):
    Top = ArrayView1D(axis=0)
    Bottom = ArrayView1D(axis=0, s_=np.s_[::-1, :])
    Left = ArrayView1D(axis=1)
    Right = ArrayView1D(axis=1, s_=np.s_[:, ::-1])


def count_trees_visible_from_outside(forest):
    views = [d.value for d in [Direction.Top, Direction.Bottom, Direction.Left, Direction.Right]]
    is_visible = apply_func_along_views(
        func=is_visible_1D,
        array=forest,
        views=views,
        aggregate_func=np.add,
    )

    return np.count_nonzero(is_visible)


def max_scenic_score(forest):
    views = [d.value for d in [Direction.Top, Direction.Bottom, Direction.Left, Direction.Right]]
    scenic_score = apply_func_along_views(
        func=n_trees_in_view_1D,
        array=forest,
        views=views,
        aggregate_func=np.multiply,
    )
    return np.amax(scenic_score)


if __name__ == "__main__":
    forest = utils.io.read_file_as_array("input/day8", int)

    print("Part I")
    print(count_trees_visible_from_outside(forest))

    print("Part II")
    print(max_scenic_score(forest))
