from typing import List, Union

import numpy as np


def read_file_lines(path: str) -> List[str]:
    with open(path) as f:
        data = f.read()
        return data.split("\n")


def read_file_as_array(path: str, dtype=float, delimiter: Union[str, int] = 1) -> np.ndarray:
    return np.genfromtxt(path, delimiter=delimiter, dtype=dtype)
