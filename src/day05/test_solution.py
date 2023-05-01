import utils.test


class TestSolution(utils.test.TestSolutionTemplate):
    def setup_class(cls):
        cls.day: int = 5

        cls.part_1_example_result = "CMZ"
        cls.part_2_example_result = "MCD"

        cls.part_1_result = "ZWHVFWQWW"
        cls.part_2_result = "HZFZCCWWV"
