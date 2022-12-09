import numpy as np

import utils.io


def is_visible_1D(line_of_trees):
    # Works on 1D array
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


def is_visible_from_outside(forest):
    flip_0 = np.s_[::-1, :]
    flip_1 = np.s_[:, ::-1]

    return (
        np.apply_along_axis(is_visible_1D, 0, forest)  # From top
        + np.apply_along_axis(is_visible_1D, 0, forest[flip_0])[flip_0]  # From bottom
        + np.apply_along_axis(is_visible_1D, 1, forest)  # From left
        + np.apply_along_axis(is_visible_1D, 1, forest[flip_1])[flip_1]  # From right
    )


def scenic_score(forest):
    flip_0 = np.s_[::-1, :]
    flip_1 = np.s_[:, ::-1]

    return (
        np.apply_along_axis(n_trees_in_view_1D, 0, forest)  # From top
        * np.apply_along_axis(n_trees_in_view_1D, 0, forest[flip_0])[flip_0]  # From bottom
        * np.apply_along_axis(n_trees_in_view_1D, 1, forest)  # From left
        * np.apply_along_axis(n_trees_in_view_1D, 1, forest[flip_1])[flip_1]  # From right
    )


if __name__ == "__main__":
    forest = utils.io.read_file_as_array("input/day8", int)

    print("Part I")
    print(np.count_nonzero(is_visible_from_outside(forest)))

    print("Part II")
    print(np.amax(scenic_score(forest)))
