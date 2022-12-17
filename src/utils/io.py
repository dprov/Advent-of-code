import re
from dataclasses import dataclass
from typing import List, Type, Union

import numpy as np


def read_file_lines(path: str, split=None, parse_as_type: Type = None) -> List[str]:
    with open(path) as f:
        data = f.read()
        data = data.split("\n")
        if split is not None:
            data = [line.split(split) for line in data]
        if parse_as_type is not None:
            data = [parse_as_type(d) for d in data]
        return data


@dataclass
class ParserClass:
    data: Union[str, List[str]]

    # Functions to define how text input is parsed, Applied in this order.

    @staticmethod
    def strip_empty_lines() -> bool:
        # Whether to remove empty lines from input before parsing
        return True

    @staticmethod
    def line_split() -> str:
        # input for str.split() applied to each line. None = no split
        return None

    @staticmethod
    def line_regex() -> str:
        # regex applied to each line. Only catch groups are kept. None = no regex matching
        # e.g. regex = "(\w{3})\w{3}(\w{3})", string = "ABCDEFGHI" --> ["ABC", "GHI"]
        return None

    @staticmethod
    def line_group_size() -> int:
        # Aggregate lines in groups of size line_group_size()
        return 1

    def parse(self):
        # Function for parsing the group of lines
        raise NotImplementedError()


def parse_file_as_type(path: str, parser_class: ParserClass) -> List:
    with open(path) as f:
        data = f.read()
        data = data.split("\n")

        if parser_class.strip_empty_lines():
            data = [d for d in data if d]

        if parser_class.line_split() is not None:
            data = [line.split(parser_class.line_split()) for line in data]

        if parser_class.line_regex() is not None:
            data = [re.match(parser_class.line_regex(), line).groups() for line in data]

        group_size = parser_class.line_group_size()
        if group_size > 1:
            data = [data[i : i + group_size] for i in range(0, len(data), group_size)]

        data = [parser_class(d).parse() for d in data]
        return data


def read_file_as_array(path: str, dtype=float, delimiter: Union[str, int] = 1) -> np.ndarray:
    return np.genfromtxt(path, delimiter=delimiter, dtype=dtype)
