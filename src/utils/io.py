from typing import List

import numpy as np


def read_file_lines(path: str) -> List[str]:
    with open(path) as f:
        data = f.read()
        return data.split("\n")


def read_file_as_array(path: str, dtype=float) -> np.ndarray:
    lines = read_file_lines(path)

    line_size = len(lines[0])
    if not all([len(l) == line_size for l in lines]):
        raise ValueError("Not all lines have equal length")

    array = np.zeros((len(lines), line_size), dtype=dtype)
    for row, line in enumerate(lines):
        for col, item in enumerate(line):
            array[row, col] = dtype(item)

    return array
