from typing import List


def read_file_lines(path: str) -> List[str]:
    with open(path) as f:
        data = f.read()
        return data.split("\n")
