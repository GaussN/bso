import os
import unittest
from functools import partial

from report_service import ReportService
from database import get_connection, init_database


class ReportTest(unittest.TestCase):
    def setUp(self):
        self.test_db_path = os.path.join(os.getcwd(), "test.sqlite3")
        self.get_connection = partial(get_connection, self.test_db_path)
        init_database(self.test_db_path)

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
                "input_data": (
                    (1, "AA"), (2, "AA"), (3, "AA"), 
                    (1, "BB"), (2, "BB"), (3, "BB")
                ),
                "expected_result": {"AA": [1, 2, 3], "BB": [1, 2, 3]},
            },
            {
                "input_data": (
                    (1, "AA"), (2, "BB"), (3, "AA"), 
                    (1, "BB"), (2, "AA"), (3, "BB")
                ),
                "expected_result": {"AA": [1, 3, 2], "BB": [2, 1, 3]},
            },
        )
        rep = ReportService(None)  # noqa
        for data in test_data:
            self.assertDictEqual(
                rep._goruped_numbers(data["input_data"]),
                data["expected_result"]
            )

    def test_get_range_valid(self):
        test_data = (
            {
                "input_data": ((1, "GG"),(2, "GG"),(3, "GG"),),
                "expected_result": {"GG": [(1,3)]}
            },
            {
                "input_data": ((1, "GG"),(3, "GG"),),
                "expected_result": {"GG": [(1, 1), (3,3)]}
            },
            {
                "input_data": (
                    (1, "GG"),(2, "GG"),
                    (5, "GG"),(15, "GG"),(16, "GG"),
                ),
                "expected_result": {"GG": [(1, 2),(5,5),(15,16)]}
            },
            {
                "input_data": (
                    (1, "GG"),(2, "GG"),(3, "GG"),
                    (2, "AA"),(3, "AA"),(4, "AA")
                ),
                "expected_result": {"GG": [(1, 3)], "AA": [(2,4)]}
            },
            {
                "input_data": ((1, "GG"), (3, "GG"),(3, "AA"), (5, "AA")),
                "expected_result": {
                    "GG": [(1, 1), (3, 3)], 
                    "AA": [(3,3), (5,5)]
                }
            },
            {
                "input_data": (
                    (1, "GG"), (2, "GG"), (5, "GG"), (15, "GG"), (16, "GG"),
                    (1, "AA"), (2, "AA"), (5, "AA"), (15, "AA"), (16, "AA"),
                ),
                "expected_result": {
                    "GG": [(1, 2), (5, 5), (15, 16)], 
                    "AA": [(1, 2), (5, 5), (15, 16)]
                }
            },
            {
                "input_data": (),
                "expected_result": {}
            },
        )
        rep = ReportService(None)  # noqa
        for data in test_data:
            self.assertDictEqual(
                rep._get_ranges(data["input_data"]),
                data["expected_result"]
            )

    def test_get_range_invalid(self):
        test_data = (
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
                "expected_result": {
                    "GG": [(1, 2), (15, 16), (5, 5)], 
                    "AA": [(5, 5), (1, 2), (15, 16)]
                },
            },
        )
        rep = ReportService(None)  # noqa
        for data in test_data:
            self.assertDictEqual(
                rep._get_ranges(data["input_data"]),
                data["expected_result"]
            )

    def test_get_bso(self):
        test_data = (
            {
                "input_data": (2024, 10), 
                "expected_result": {
                    "use": {"AA": [(1, 3), (5, 5), (7, 7)]},
                    "new": {"AA": [(1, 9)]},
                    "spoiled": {"AA": [(4, 4)]},
                    "lost": {"AA": [(6, 6)]},
                    "clean_at_begin": {},
                    "clean_at_end": {"AA": [(8, 9)]},
                }
            },
            {
                "input_data": (2024, 11),
                "expected_result": {
                    "use": {"AA": [(8, 8)], "AB": [(1, 3), (5, 7), (9, 9)]},
                    "new": {"AB": [(1, 9)]},
                    "spoiled": {"AA": [(9, 9)], "AB": [(4, 4)]},
                    "lost": {},
                    "clean_at_begin": {"AA": [(8, 9)]},
                    "clean_at_end": {"AB": [(8, 8)]}
                }
            },
            {   
                "input_data": (2024, 12),
                "expected_result": {
                    "use": {"AC": [(1, 2), (4, 4), (6, 12)]},
                    "new": {"AC": [(1, 19)]},
                    "spoiled": {"AB": [(8, 8)], "AC": [(5, 5)]},
                    "lost": {"AC": [(3, 3)]},
                    "clean_at_begin": {"AB": [(8, 8)]},
                    "clean_at_end": {"AC": [(13, 19)]},
                }
            },
            {   
                "input_data": (2025, 1),
                "expected_result": {
                    "use": {
                        "AC": [(13, 13), (15, 15), (17, 19)], 
                        "AD": [(1, 1)]
                    },
                    "new": {"AD": [(1, 9)]},
                    "spoiled": {"AC": [(14, 14), (16, 16)]},
                    "lost": {},
                    "clean_at_begin": {"AC": [(13, 19)]},
                    "clean_at_end": {"AD": [(2, 9)]},
                }
            },
            {   
                "input_data": (2025, 2),
                "expected_result": {
                    "use": {"AD": [(2, 3), (5, 5)]},
                    "new": {"AE": [(1, 9)]},
                    "spoiled": {"AD": [(4, 4)]},
                    "lost": {},
                    "clean_at_begin": {"AD": [(2, 9)]},
                    "clean_at_end": {"AD": [(6, 9)], "AE": [(1, 9)]},
                }
            },
            {    
                "input_data": (2025, 3),
                "expected_result": {
                    "use": {},
                    "new": {},
                    "spoiled": {},
                    "lost": {},
                    "clean_at_begin": {"AD": [(6, 9)], "AE": [(1, 9)]},
                    "clean_at_end": {"AD": [(6, 9)], "AE": [(1, 9)]},
                }
            },
            {  
                "input_data": (2013, 1),
                "expected_result": {
                    "use": {},
                    "new": {},
                    "spoiled": {},
                    "lost": {},
                    "clean_at_begin": {},
                    "clean_at_end": {},
                }
            },
        )
        with open("sql/insert_test_data.sql", "r") as file:
            script = file.read()
        with self.get_connection() as conn:
            conn.executescript(script)
            conn.commit()

        rep = ReportService(self.get_connection)
        for data in test_data:
            self.assertDictEqual(
                rep.get_report(*data["input_data"]),
                data["expected_result"]
            )

    def tearDown(self):
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
