import importlib
import os
from typing import Callable, Dict, Union

import pytest

Result = Union[str, int]


class TestSolutionTemplate:
    day: int = None

    part_1_example_result: Result = None
    part_2_example_result: Result = None

    part_1_result: Result = None
    part_2_result: Result = None

    part_1_example_kwargs: Dict = {}
    part_2_example_kwargs: Dict = {}
    part_1_kwargs: Dict = {}
    part_2_kwargs: Dict = {}

    def _init_members(self):
        self.day_string = (
            None if self.day is None else f"day0{self.day}" if self.day <= 9 else f"day{self.day}"
        )

        self.example_file = None if self.day is None else f"example_input/{self.day_string}.txt"
        self.input_file = None if self.day is None else f"input/{self.day_string}.txt"

        self.solution = (
            None if self.day is None else importlib.import_module(f"{self.day_string}.solution")
        )

        self.part_1_solver: Callable[[str], int] = (
            None if self.solution is None else self.solution.solve_part_1
        )
        self.part_2_solver: Callable[[str], int] = (
            None if self.solution is None else self.solution.solve_part_2
        )

    @classmethod
    def setup_class(cls):
        """Setup function called before member test functions. Should be defined in derived classes to set test results or override default members"""
        raise NotImplementedError()

    # Done tis way instead of using @pytest.mark.parametrize decorator due to repetitive nature of tests with fixed input files and output format
    def _run_test(
        self,
        solver: Callable[[str], int] = None,
        input_file: str = None,
        solver_kwargs: Dict = {},
        result: int = None,
    ) -> None:
        if solver is None or not os.path.exists(input_file) or result is None:
            pytest.skip("Test not configured")
        else:
            assert solver(input_file, **solver_kwargs) == result

    def test_part_1_example(self):
        self._init_members()
        self._run_test(
            solver=self.part_1_solver,
            input_file=self.example_file,
            solver_kwargs=self.part_1_example_kwargs,
            result=self.part_1_example_result,
        )

    def test_part_1(self):
        self._init_members()
        self._run_test(
            solver=self.part_1_solver,
            input_file=self.input_file,
            solver_kwargs=self.part_1_kwargs,
            result=self.part_1_result,
        )

    def test_part_2_example(self):
        self._init_members()
        self._run_test(
            solver=self.part_2_solver,
            input_file=self.example_file,
            solver_kwargs=self.part_2_example_kwargs,
            result=self.part_2_example_result,
        )

    def test_part_2(self):
        self._init_members()
        self._run_test(
            solver=self.part_2_solver,
            input_file=self.input_file,
            solver_kwargs=self.part_2_kwargs,
            result=self.part_2_result,
        )
