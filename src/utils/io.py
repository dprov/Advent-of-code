import re
from dataclasses import dataclass
from typing import Any, Callable, List, Type, Union

import numpy as np

InputData = Union[str, List[str]]

InputDataList = List[InputData]


def read_file_lines(path: str, split: str = None, parse_as_type: Type = None) -> InputDataList:
    """Reads all lines of a text file independently

    Args:
        path (str): file path
        split (str, optional): Separator used on each line. Defaults to None (not split).
        parse_as_type (Type, optional): Create an object of this type with each (optionally separated) line. Defaults to None (not parsed as type).

    Returns:
        StrContainer: List with each item being a string (if not separator) or list of separated strings from a single line
    """
    with open(path) as f:
        data = f.read()
        data = data.split("\n")
        if split is not None:
            data = [line.split(split) for line in data]
        if parse_as_type is not None:
            data = [parse_as_type(d) for d in data]
        return data


def read_file_as_array(
    path: str, dtype: Type = float, delimiter: Union[str, int] = 1
) -> np.ndarray:
    """Read file as numpy array

    Args:
        path (str): file path
        dtype (Type, optional): Data type. Defaults to float.
        delimiter (Union[str, int], optional): . Defaults to 1.

    Returns:
        np.ndarray: Array read from file
    """
    return np.genfromtxt(path, delimiter=delimiter, dtype=dtype)


@dataclass
class FileParser:
    data: InputDataList

    def __init__(
        self,
        data_parser: Callable[[InputData], Any],
        strip_empty_lines: bool = True,
        line_sep: str = None,
        line_regex: str = None,
        line_group_size: int = 1,
    ) -> None:
        """
        Init method. Defines operations applied to file lines to group/split/etc. them into data chunks that are then parsed
        Args:
            data_parser (Callable[[StrData],Any]): Function parsing aggregated/processed data chunks into an object. (i.e. how to parse data chunks,
                data chunk being defined from other arguments)
            strip_empty_lines (bool, optional): Whether to remove empty lines from input before parsing. Defaults to True.
            line_sep (str, optional): input for str.split() applied to each line. Defaults to None (no split).
            line_regex (str, optional): regex applied to each line. Only catch groups are kept.
                e.g. regex = "(\w{3})\w{3}(\w{3})", string = "ABCDEFGHI" --> ["ABC", "GHI"].
                Defaults to None (no regex matching)
            line_group_size (int, optional): _description_. Defaults to 1.
        """
        self.data_parser = data_parser
        self.strip_empty_lines = strip_empty_lines
        self.line_sep = line_sep
        self.line_regex = line_regex
        self.line_group_size = line_group_size

    def parse_file(self, path: str) -> List[Any]:
        """Parse file using current configuration.

        Args:
            path (str): Path to file

        Returns:
            List[Any]: List of objects, obtained from parsing all aggregated/processed groups of lines in the input file
        """
        with open(path) as f:
            data = f.read()
            data = data.split("\n")

            if self.strip_empty_lines:
                data = [d for d in data if d]

            if self.line_sep is not None:
                data = [line.split(self.line_sep) for line in data]

            if self.line_regex is not None:
                data = [re.match(self.line_regex, line).groups() for line in data]

            group_size = self.line_group_size
            if group_size > 1:
                data = [data[i : i + group_size] for i in range(0, len(data), group_size)]

            data = [self.data_parser(d) for d in data]
            return data
