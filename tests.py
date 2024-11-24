import os
import unittest

from report_service import ReportService
from database import get_connection, init_database


class ReportTest(unittest.TestCase):
    def setUp(self):
        # self.test_db_path = os.path.join(os.getcwd(), "test.sqlite3")
        # self.get_connection = lambda: get_connection(self.test_db_path)
        # init_database(self.test_db_path)
        pass

    def test_normalize_ranges(self):
        test_data = (
            {
                "input_data": tuple(),
                "expected_result": {},
            },
            {
                "input_data": ((1,"AA"),),
                "expected_result": {"AA": [1]},
            },
            {
                "input_data": ((1, "AA"), (3, "AA"), (4, "AA")),
                "expected_result": {"AA": [1, 3, 4]},
            },
            {
                "input_data": ((1, "AA"), (2, "AA"), (3, "AA"), (1, "BB"), (2, "BB"), (3, "BB")),
                "expected_result": {"AA": [1, 2, 3], "BB": [1, 2, 3]},
            },
            {
                "input_data": ((1, "AA"), (2, "BB"), (3, "AA"), (1, "BB"), (2, "AA"), (3, "BB")),
                "expected_result": {"AA": [1, 3, 2], "BB": [2, 1, 3]},
            },
        )
        rep = ReportService(None)  # noqa
        for data in test_data:
            self.assertDictEqual(
                rep._ReportService__get_numbers_by_series(data["input_data"]),
                data["expected_result"]
            )

    def test_get_range_valid(self):
        tests_valid_data = (
            {
                "input_data": ((1, "GG"),(2, "GG"),(3, "GG"),),
                "expected_result": {"GG": [(1,3)]}
            },
            {
                "input_data": ((1, "GG"),(3, "GG"),),
                "expected_result": {"GG": [(1, 1), (3,3)]}
            },
            {
                "input_data": ((1, "GG"),(2, "GG"),(5, "GG"),(15, "GG"),(16, "GG"),),
                "expected_result": {"GG": [(1, 2),(5,5),(15,16)]}
            },
            {
                "input_data": ((1, "GG"), (2, "GG"), (3, "GG"),(2, "AA"),(3, "AA"),(4, "AA")),
                "expected_result": {"GG": [(1, 3)], "AA": [(2,4)]}
            },
            {
                "input_data": ((1, "GG"), (3, "GG"),(3, "AA"), (5, "AA")),
                "expected_result": {"GG": [(1, 1), (3, 3)], "AA": [(3,3), (5,5)]}
            },
            {
                "input_data": (
                    (1, "GG"), (2, "GG"), (5, "GG"), (15, "GG"), (16, "GG"),
                    (1, "AA"), (2, "AA"), (5, "AA"), (15, "AA"), (16, "AA"),
                ),
                "expected_result": {"GG": [(1, 2), (5, 5), (15, 16)], "AA": [(1, 2), (5, 5), (15, 16)]}
            },
            {
                "input_data": (),
                "expected_result": {}
            },
        )
        rep = ReportService(None)  # noqa
        for data in tests_valid_data:
            self.assertDictEqual(
                rep._ReportService__get_ranges(data["input_data"]),
                data["expected_result"]
            )

    def test_get_range_invalid(self):
        tests_valid_data = (
            {
                "input_data": ((3, "GG"), (2, "GG"), (1, "GG"),),
                "expected_result": {"GG": [(3, 3), (2, 2), (1, 1)]},
            },
            {
                "input_data": ((1, "GG"), (2, "GG"), (1, "GG"),),
                "expected_result": {"GG": [(1, 2), (1, 1)]},
            },
            {
                "input_data": ((1, "GG"), (3, "GG"), (1, "GG"),),
                "expected_result": {"GG": [(1, 1), (3, 3), (1, 1)]},
            },
            {
                "input_data": (
                    (1, "GG"), (2, "GG"), (5, "AA"), (15, "GG"), (16, "GG"),
                    (1, "AA"), (2, "AA"), (5, "GG"), (15, "AA"), (16, "AA"),
                ),
                "expected_result": {"GG": [(1, 2), (15, 16), (5, 5)], "AA": [(5, 5), (1, 2), (15, 16)]},
            },
        )
        rep = ReportService(None)  # noqa
        for data in tests_valid_data:
            self.assertDictEqual(
                rep._ReportService__get_ranges(data["input_data"]),
                data["expected_result"]
            )

    def tearDown(self):
        pass  # os.remove(self.test_db_path)



if __name__ == "__main__":
    unittest.main()