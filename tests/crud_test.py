import os
import sqlite3
import unittest 
import datetime as dt
from functools import partial

import blanks.models as models
import blanks.crud as crud
from database import init_database, get_connection


class BlankAdapterTest(unittest.TestCase):
    def test_to_dict(self):
        input = models.BlankInDTO(date=dt.date(2024,12,12), series="AF", number=1)
        res = crud.BlankAdapter.to_dict(input)
        excepted = {
            "date": "2024-12-12 00:00:00", "series": "AF", 
            "number": 1, "comment": "", "status": 0
        }
        self.assertDictEqual(
            res,
            excepted
        )

    def test_from_dict_none(self):
        input = None
        res = crud.BlankAdapter.from_dict(input)
        self.assertIsNone(res)

    def test_from_dict(self):
        input = {
            "date": "2024-12-12 00:00:00",
            "series": "AF",
            "number": 1,
            "comment": "",
            "status": 0,
            "created_at": "2024-12-12 00:00:00",
            "updated_at": "2024-12-13 00:00:00",
            "deleted_at": None,
        }
        res = crud.BlankAdapter.from_dict(input)
        excepted = models.BlankOutDTO(
            date=dt.date(2024,12,12),
            series="AF",
            number=1,
            created_at=dt.date(2024,12,12),
            updated_at=dt.date(2024,12,13),
        )
        self.assertTrue(res.full_compare(excepted))


class BlanksCRUDTest(unittest.TestCase):
    def setUp(self):
        self.test_db_path = os.path.join(os.getcwd(), "test.sqlite3")
        self.get_connection = partial(get_connection, self.test_db_path)
        self.crud = crud.BlankCRUD(self.get_connection)
        init_database(self.test_db_path)

    def tearDown(self):
        os.remove(self.test_db_path)

    def test_get(self):
        with self.get_connection() as conn:
            conn.execute("INSERT INTO blanks(id, series, number) VALUES(1, 'AF', 1)")
            conn.execute("INSERT INTO blanks(id, series, number) VALUES(2, 'AF', 2)")
            conn.execute("INSERT INTO blanks(id, series, number) VALUES(3, 'AF', 3)")
            conn.commit()
        self.assertEqual(models.BlankInDTO(series="AF", number=1), self.crud.get(1))
        self.assertEqual(models.BlankInDTO(series="AF", number=2), self.crud.get(2))
        self.assertEqual(models.BlankInDTO(series="AF", number=3), self.crud.get(3))
        self.assertIsNone(self.crud.get(4))

    def test_read_with_filter(self):
        with self.get_connection() as conn:
            conn.execute("INSERT INTO blanks(id, series, number) VALUES(1, 'AF', 1)")
            conn.execute("INSERT INTO blanks(id, series, number) VALUES(2, 'AA', 2)")
            conn.execute("INSERT INTO blanks(id, series, number) VALUES(3, 'AF', 3)")
            conn.commit()
        expected_result = [
            models.BlankInDTO(series="AF", number=1),
            models.BlankInDTO(series="AF", number=3),
        ]
        self.assertListEqual(expected_result, self.crud.read_with_filter("WHERE series=?", ("AF",)))

    def test_read(self):
        with self.get_connection() as conn:
            conn.execute("INSERT INTO blanks(id, series, number) VALUES(1, 'AF', 1)")
            conn.execute("INSERT INTO blanks(id, series, number) VALUES(2, 'AF', 2)")
            conn.execute("INSERT INTO blanks(id, series, number) VALUES(3, 'AF', 3)")
            conn.commit()
        expected_result = [
            models.BlankInDTO(series="AF", number=1),
            models.BlankInDTO(series="AF", number=2),
            models.BlankInDTO(series="AF", number=3),
        ]
        self.assertListEqual(expected_result, self.crud.read())

    def test_read_empty(self):
        self.assertListEqual([], self.crud.read())

    def test_create_one(self):
        new_blank = models.BlankInDTO(series="AF", number=1)
        self.crud.create(new_blank)
        self.assertEqual(new_blank, self.crud.get(1))

    def test_create_seq(self):
        new_blanks = [
            models.BlankInDTO(series="AF", number=1),
            models.BlankInDTO(series="AF", number=2),
            models.BlankInDTO(series="AF", number=3),
        ]
        self.crud.create(new_blanks)
        self.assertListEqual(new_blanks, self.crud.read())

    def test_create_from_range(self):
        blanks_range = models.BlankRangeInDTO(series="AF", start=100, end=115)
        expected_result = [models.BlankInDTO(series="AF", number=n) for n in blanks_range.get_range()]
        self.crud.create_from_range(blanks_range)
        self.assertListEqual(
            expected_result, 
            self.crud.read()
        )

    def test_update(self):
        blank = models.BlankInDTO(series="AF", number=1, comment="gapan")
        self.crud.create(blank)
        self.crud.update(models.BlankUpdateDTO(id=1, comment="gena"))
        updated_blank = self.crud.get(1)
        self.assertEqual(updated_blank.comment, "gena")

    def test_delete(self):
        blank = models.BlankInDTO(series="AF", number=1)
        cur = self.crud.create(blank)
        cur: sqlite3.Cursor
        self.assertIsNotNone(self.crud.get(1))
        self.crud.delete(1)
        self.assertIsNotNone(self.crud.get(1))