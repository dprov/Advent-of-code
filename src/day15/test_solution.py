import utils.test


class TestSolution(utils.test.TestSolutionTemplate):
    def setup_class(cls):
        cls.day: int = 15

        cls.part_1_example_result = 26
        cls.part_1_example_kwargs = {"row": 10}

        cls.part_2_example_result = 56000011
        cls.part_2_example_kwargs = {"grid_size": 20}

        cls.part_1_result = 5125700
        cls.part_1_kwargs = {"row": 2000000}

        cls.part_2_result = 11379394658764
        cls.part_2_kwargs = {"grid_size": 4000000}
