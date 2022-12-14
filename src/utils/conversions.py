import numpy as np


def get_char_value_str(c: str, min_value: int = 0) -> str:
    if c.islower():
        return str(ord(c) - ord("a") + min_value)
    else:
        return str(ord(c) - ord("A") + min_value + 26)


def alpha_array_to_int(array: np.ndarray, min_value: int = 0) -> str:
    if array.dtype != "<U1":
        raise ValueError("Input must be char array")
    int_array = array.view(np.int32).copy()
    is_lower = np.greater_equal(int_array, ord("a")) * np.less_equal(int_array, ord("z"))
    is_upper = np.greater_equal(int_array, ord("A")) * np.less_equal(int_array, ord("Z"))
    if not np.all(is_upper + is_lower):
        raise ValueError("Array does not contain only chars")

    int_array += (min_value - ord("a")) * is_lower + (min_value + 26 - ord("A")) * is_upper

    return int_array
