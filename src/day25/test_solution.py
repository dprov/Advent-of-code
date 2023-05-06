import utils.test


class TestSolution(utils.test.TestSolutionTemplate):
    def setup_class(cls):
        cls.day: int = 25

        cls.part_1_example_result = "2=-1=0"
        cls.part_2_example_result = None

        cls.part_1_result = "2-=2==00-0==2=022=10"
        cls.part_2_result = None
