import os
import sqlite3
import unittest 
import datetime as dt

import src.web.models as models
import src.web.blank_crud as crud
from src.database import init_database, gget_connection

import loggers


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


class GetUpdateStmtTest(unittest.TestCase):
    def test_get_update_stmt(self):
        update_blank = models.BlankUpdateDTO(id=1, comment="gena", status=models.BlankState.Use)
        print(update_blank.get_update_stmt())


class BlanksCRUDTest(unittest.TestCase):
    def setUp(self):
        self._db_path = "test.sqlite3"
        self._get_connection = gget_connection(self._db_path)
        self._bcrud = crud.BlankCRUD(self._get_connection)
        init_database(self._db_path)

    def tearDown(self):
        os.remove(self._db_path)

    def test_get(self):
        with self._get_connection() as conn:
            conn.execute("INSERT INTO blanks(id, series, number) VALUES(1, 'AF', 1)")
            conn.execute("INSERT INTO blanks(id, series, number) VALUES(2, 'AF', 2)")
            conn.execute("INSERT INTO blanks(id, series, number) VALUES(3, 'AF', 3)")
            conn.commit()
        self.assertEqual(models.BlankInDTO(series="AF", number=1), self._bcrud.get(1))
        self.assertEqual(models.BlankInDTO(series="AF", number=2), self._bcrud.get(2))
        self.assertEqual(models.BlankInDTO(series="AF", number=3), self._bcrud.get(3))
        self.assertIsNone(self._bcrud.get(4))

    def test_read_with_filter(self):
        with self._get_connection() as conn:
            conn.execute("INSERT INTO blanks(id, series, number) VALUES(1, 'AF', 1)")
            conn.execute("INSERT INTO blanks(id, series, number) VALUES(2, 'AA', 2)")
            conn.execute("INSERT INTO blanks(id, series, number) VALUES(3, 'AF', 3)")
            conn.commit()
        expected_result = [
            models.BlankInDTO(series="AF", number=1),
            models.BlankInDTO(series="AF", number=3),
        ]
        self.assertListEqual(expected_result, self._bcrud.read_with_filter("WHERE series=?", ("AF",)))

    def test_read(self):
        with self._get_connection() as conn:
            conn.execute("INSERT INTO blanks(id, series, number) VALUES(1, 'AF', 1)")
            conn.execute("INSERT INTO blanks(id, series, number) VALUES(2, 'AF', 2)")
            conn.execute("INSERT INTO blanks(id, series, number) VALUES(3, 'AF', 3)")
            conn.commit()
        expected_result = [
            models.BlankInDTO(series="AF", number=1),
            models.BlankInDTO(series="AF", number=2),
            models.BlankInDTO(series="AF", number=3),
        ]
        self.assertListEqual(expected_result, self._bcrud.read())

    def test_read_empty(self):
        self.assertListEqual([], self._bcrud.read())

    def test_create_one(self):
        new_blank = models.BlankInDTO(series="AF", number=1)
        self._bcrud.create(new_blank)
        print(f"{new_blank=}")
        print(f"{self._bcrud.get(1)=}")
        self.assertEqual(new_blank, self._bcrud.get(1))

    def test_create_seq(self):
        new_blanks = [
            models.BlankInDTO(series="AF", number=1),
            models.BlankInDTO(series="AF", number=2),
            models.BlankInDTO(series="AF", number=3),
        ]
        self._bcrud.create(new_blanks)
        self.assertListEqual(new_blanks, self._bcrud.read())

    def test_update(self):
        blank = models.BlankInDTO(series="AF", number=1, comment="gapan")
        self._bcrud.create(blank)
        self._bcrud.update(models.BlankUpdateDTO(id=1, comment="gena"))
        updated_blank = self._bcrud.get(1)
        self.assertEqual(updated_blank.comment, "gena")

    def test_delete(self):
        blank = models.BlankInDTO(series="AF", number=1)
        cur = self._bcrud.create(blank)
        cur: sqlite3.Cursor
        self.assertIsNotNone(self._bcrud.get(1))
        self._bcrud.delete(1)
        self.assertIsNotNone(self._bcrud.get(1))