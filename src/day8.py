from dataclasses import dataclass
from enum import Enum
from typing import Callable, List

import numpy as np
from numpy.lib.index_tricks import IndexExpression

import utils.io


# Utils for applying 1D processing function along multiple directions on a 2D array
@dataclass
class ArrayView1D:
    axis: int
    s_: IndexExpression = np.s_[:, :]


class Direction(Enum):
    Top = ArrayView1D(axis=0)
    Bottom = ArrayView1D(axis=0, s_=np.s_[::-1, :])
    Left = ArrayView1D(axis=1)
    Right = ArrayView1D(axis=1, s_=np.s_[:, ::-1])


def apply_along_directions(
    x: np.ndarray, func: Callable, directions: List[Direction], aggregate_func: Callable
):
    if not directions:
        raise ValueError("No directions to apply")

    view: ArrayView1D = directions[0].value
    result = np.apply_along_axis(func, view.axis, forest[view.s_])[view.s_]

    for dir in directions[1:]:
        view = dir.value
        result = aggregate_func(
            result, np.apply_along_axis(func, view.axis, forest[view.s_])[view.s_]
        )

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
    # Works on 1D array
    trees_in_view = np.zeros(line_of_trees.shape, dtype=int)

    # First tree cannot see any tree
    n_visible_per_height = np.zeros((10,), dtype=int)
    for ind, tree in enumerate(line_of_trees):
        trees_in_view[ind] += n_visible_per_height[tree]

        # Any trees smaller or equal can now only see this tree
        if tree > 0:
            n_visible_per_height[0 : tree + 1] = 1

        # Taller trees see one more tree
        if tree < 9:
            n_visible_per_height[tree + 1 :] += 1

    return trees_in_view


# Functions for solving
def count_trees_visible_from_outside(forest):
    is_visible = apply_along_directions(
        forest,
        func=is_visible_1D,
        directions=[Direction.Top, Direction.Bottom, Direction.Left, Direction.Right],
        aggregate_func=np.add,
    )

    return np.count_nonzero(is_visible)


def max_scenic_score(forest):
    scenic_score = apply_along_directions(
        forest,
        func=n_trees_in_view_1D,
        directions=[Direction.Top, Direction.Bottom, Direction.Left, Direction.Right],
        aggregate_func=np.multiply,
    )
    return np.amax(scenic_score)


if __name__ == "__main__":
    forest = utils.io.read_file_as_array("input/day8", int)

    print("Part I")
    print(count_trees_visible_from_outside(forest))

    print("Part II")
    print(max_scenic_score(forest))
