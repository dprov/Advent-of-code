from __future__ import annotations

import re
from typing import Union

import anytree

import utils.io


# Node class for filesystem tree
class FilesystemNode(anytree.Node):
    def __init__(
        self, name, is_dir: bool, file_size: int = 0, parent=None, children=None, **kwargs
    ):
        super().__init__(
            name, parent, children, is_dir=is_dir, file_size=0 if is_dir else file_size, **kwargs
        )

    def get_child_with_name(self, name: str) -> FilesystemNode:
        children_names = [c.name for c in self.children]
        try:
            child_ind = children_names.index(name)
            return self.children[child_ind]
        except ValueError:
            return None


# Tree utils
def get_root_node(node: FilesystemNode) -> FilesystemNode:
    curr_node = node
    while curr_node.parent != None:
        curr_node = curr_node.parent
    return curr_node


def print_tree(root: FilesystemNode):
    for pre, fill, node in anytree.RenderTree(root):
        print(f"{pre}{node.name}  {node.file_size}")


# Classes for representing input
class FileInfo:
    def __init__(self, output: str) -> None:
        m = re.match("(\d+) (\w+\.?\w*)", output)
        if m is None:
            raise ValueError("Command mismatch")
        self.size = int(m.group(1))
        self.name = m.group(2)

    def to_node(self, parent: FilesystemNode = None) -> FilesystemNode:
        node = FilesystemNode(name=self.name, is_dir=False, file_size=self.size, parent=parent)
        curr_node = node
        while curr_node.parent != None:
            curr_node = curr_node.parent
            if curr_node.is_dir:
                curr_node.file_size += node.file_size
        return


class DirInfo:
    def __init__(self, output: str) -> None:
        m = re.match("dir (\w+)", output)
        if m is None:
            raise ValueError("Command mismatch")
        self.name = m.group(1)

    def to_node(self, parent: FilesystemNode = None) -> FilesystemNode:
        return FilesystemNode(name=self.name, is_dir=True, parent=parent)


class CDcmd:
    def __init__(self, command: str) -> None:
        if command[0:5] != "$ cd ":
            raise ValueError("Command mismatch")
        self.arg = command[5:]

    def apply(self, node: FilesystemNode) -> FilesystemNode:
        if self.arg == "/":
            return get_root_node(node)
        elif self.arg == "..":
            return node.parent
        else:
            child = node.get_child_with_name(self.arg)
            if child is None:
                child = FilesystemNode(name=self.arg, is_dir=True, parent=node)
            return child


class LScmd:
    def __init__(self, command: str) -> None:
        if command != "$ ls":
            raise ValueError("Command mismatch")
        self.results = []

    def add_output(self, result: Union[FileInfo, DirInfo]):
        self.results.append(result)

    def apply(self, parent: FilesystemNode) -> None:
        for result in self.results:
            # If node not already in children, create
            if parent.get_child_with_name(result.name) == None:
                result.to_node(parent=parent)


# Functions for parsing input
def parse_output(output: str) -> Union[FileInfo, DirInfo]:
    if output[0:3] == "dir":
        return DirInfo(output)
    else:
        return FileInfo(output)


def parse_command(command: str) -> Union[LScmd, CDcmd]:
    if command[0:5] == "$ ls":
        return LScmd(command)
    else:
        return CDcmd(command)


def parse_line(line: str) -> Union[LScmd, CDcmd, FileInfo, DirInfo]:
    if line[0] == "$":
        return parse_command(line)
    else:
        return parse_output(line)


def build_filesystem_from_input(input_file: str) -> FilesystemNode:
    data = utils.io.read_file_lines(input_file)

    current_ls_cmd: LScmd = None
    curr_node = FilesystemNode(name="/", is_dir=True)
    for line in data:
        print_tree(get_root_node(curr_node))
        item = parse_line(line)
        if isinstance(item, FileInfo) or isinstance(item, DirInfo):
            if not isinstance(current_ls_cmd, LScmd):
                raise RuntimeError()
            current_ls_cmd.add_output(item)
        else:
            if current_ls_cmd is not None:
                current_ls_cmd.apply(curr_node)
                current_ls_cmd = None
            if isinstance(item, CDcmd):
                curr_node = item.apply(curr_node)
            elif isinstance(item, LScmd):
                current_ls_cmd = item
            else:
                raise NotImplementedError()
    if current_ls_cmd is not None:
        current_ls_cmd.apply(curr_node)

    return get_root_node(curr_node)


# Functions for solving
def sum_dir_sizes(root: FilesystemNode, max_dir_size: int) -> int:
    file_sizes = [
        node.file_size
        for node in anytree.PreOrderIter(root)
        if node.is_dir and node.file_size <= max_dir_size
    ]
    return sum(file_sizes)


def find_min_dir_size_greater_than(root: FilesystemNode, min_valid_size: int) -> int:
    file_sizes = [
        node.file_size
        for node in anytree.PreOrderIter(root)
        if node.is_dir and node.file_size >= min_valid_size
    ]

    return min(file_sizes)


def get_dir_to_remove_size(root: FilesystemNode, total_space: int, min_space_needed: int):
    used_space = root.file_size
    free_space = total_space - used_space
    space_to_free = min_space_needed - free_space
    if space_to_free <= 0:
        return None

    return find_min_dir_size_greater_than(root, space_to_free)


def solve_part_1(input_file: str) -> int:
    root = build_filesystem_from_input(input_file)
    return sum_dir_sizes(root, max_dir_size=100000)


def solve_part_2(input_file: str) -> int:
    root = build_filesystem_from_input(input_file)
    return get_dir_to_remove_size(root, total_space=int(7e7), min_space_needed=int(3e7))


if __name__ == "__main__":
    print("Part I")
    print(solve_part_1("input/day7.txt"))

    print("Part II")
    print(solve_part_2("input/day7.txt"))
