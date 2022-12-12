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

    def parse(self):
        raise NotImplementedError()

    @staticmethod
    def line_split() -> str:
        return NotImplementedError()


def parse_file_as_type(path: str, parser_class: ParserClass) -> List:
    with open(path) as f:
        data = f.read()
        data = data.split("\n")
        if parser_class.line_split() is not None:
            data = [line.split(parser_class.line_split()) for line in data]
        data = [parser_class(d).parse() for d in data]
        return data


def read_file_as_array(path: str, dtype=float, delimiter: Union[str, int] = 1) -> np.ndarray:
    return np.genfromtxt(path, delimiter=delimiter, dtype=dtype)
