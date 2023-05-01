import utils.test


class TestSolution(utils.test.TestSolutionTemplate):
    def setup_class(cls):
        cls.day: int = 1

        cls.part_1_example_result = 24000
        cls.part_2_example_result = 45000

        cls.part_1_result = 71924
        cls.part_2_result = 210406
