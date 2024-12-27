import os
import sqlite3
import unittest 
import datetime
from random import random
from functools import partial

import loggers
from blanks.crud import BlankAdapter, BlankCRUD
from database import init_database, get_connection
from blanks.models import BlankStatus
from blanks.models import BlankOutDTO
from blanks.models import BlankUpdateDTO, Undefined
from blanks.models import BlankInDTO, BlankRangeInDTO


class BlankAdapterTest(unittest.TestCase):
    def test_to_dict(self):
        input_ = BlankInDTO(
            date=datetime.date(2024,12,12), 
            series="AF", 
            number=1, 
            status=BlankStatus.Clean
        )
        res = BlankAdapter.to_dict(input_)
        excepted = {
            "date": "2024-12-12 00:00:00", "series": "AF", 
            "number": 1, "comment": "", "status": 0
        }
        self.assertDictEqual(
            res,
            excepted
        )

    def test_from_dict_none(self):
        input_ = None
        res = BlankAdapter.from_dict(input_)
        self.assertIsNone(res)

    def test_from_dict(self):
        input_ = {
            "date": "2024-12-12 00:00:00",
            "series": "AF",
            "number": 1,
            "comment": "",
            "status": 0,
            "created_at": "2024-12-12 00:00:00",
            "updated_at": "2024-12-13 00:00:00",
            "deleted_at": None,
        }
        res = BlankAdapter.from_dict(input_)
        excepted = BlankOutDTO(
            date=datetime.date(2024,12,12),
            series="AF",
            number=1,
            status=BlankStatus.Clean,
            created_at=datetime.date(2024,12,12),
            updated_at=datetime.date(2024,12,13),
        )
        self.assertTrue(res.full_compare(excepted))


class BlanksCRUDTest(unittest.TestCase):
    def setUp(self):
        self.test_db_path = os.path.join(
            os.getcwd(), 
            f"{random()*1000}.sqlite3"
        )
        self.get_connection = partial(get_connection, self.test_db_path)
        self.crud = BlankCRUD(self.get_connection)
        init_database(self.test_db_path)

    def tearDown(self):
        os.remove(self.test_db_path)

    def test_get(self):
        with self.get_connection() as conn:
            conn.executemany(
                "INSERT INTO blanks(id, series, number) VALUES(?,?,?)",
                ((1,"AF", 1),(2,"AF", 2),(3,"AF", 3),)
            )
            conn.commit()
        self.assertEqual(BlankInDTO(series="AF", number=1), self.crud.get(1))
        self.assertEqual(BlankInDTO(series="AF", number=2), self.crud.get(2))
        self.assertEqual(BlankInDTO(series="AF", number=3), self.crud.get(3))
        self.assertIsNone(self.crud.get(4))

    def test_read_with_filter(self):
        with self.get_connection() as conn:
            conn.executemany(
                "INSERT INTO blanks(id, series, number) VALUES(?,?,?)",
                ((1,"AF", 1),(2,"AA", 2),(3,"AF", 3),)
            )
            conn.commit()
        expected_result = [
            BlankInDTO(series="AF", number=1),
            BlankInDTO(series="AF", number=3),
        ]
        self.assertListEqual(
            expected_result, 
            self.crud.read_with_filter("WHERE series=?", ("AF",))
        )

    def test_read(self):
        with self.get_connection() as conn:
            conn.executemany(
                "INSERT INTO blanks(id, series, number) VALUES(?,?,?)",
                ((1,"AF", 1),(2,"AF", 2),(3,"AF", 3),)
            )
            conn.commit()
        expected_result = [
            BlankInDTO(series="AF", number=1),
            BlankInDTO(series="AF", number=2),
            BlankInDTO(series="AF", number=3),
        ]
        self.assertListEqual(expected_result, self.crud.read())

    def test_read_empty(self):
        self.assertListEqual([], self.crud.read())

    def test_create_one(self):
        new_blank = BlankInDTO(series="AF", number=1)
        self.crud._create(new_blank)
        self.assertEqual(new_blank, self.crud.get(1))

    def test_create_seq(self):
        new_blanks = [
            BlankInDTO(series="AF", number=1),
            BlankInDTO(series="AF", number=2),
            BlankInDTO(series="AF", number=3),
        ]
        self.crud._create(new_blanks)
        self.assertListEqual(new_blanks, self.crud.read())

    def test_create_from_range(self):
        blanks_range = BlankRangeInDTO(series="AF", start=100, end=115)
        expected_result = [
            BlankInDTO(series="AF", number=n) 
            for n in blanks_range.get_range()
        ]
        self.crud.create_from_range(blanks_range)
        self.assertListEqual(
            expected_result, 
            self.crud.read()
        )

    def test_update_comment(self):
        blank = BlankInDTO(series="AF", number=1, comment="gapan")
        self.crud._create(blank)
        self.crud.update(BlankUpdateDTO(id=1, comment="gena"))
        updated_blank = self.crud.get(1)
        self.assertEqual(updated_blank.number, 1)
        self.assertEqual(updated_blank.comment, "gena")

    def test_update_status(self):
        blank = BlankInDTO(series="AF", number=1)
        self.crud._create(blank)
        self.crud.update(BlankUpdateDTO(id=1, status=BlankStatus.Lost))
        updated_blank = self.crud.get(1)
        self.assertEqual(updated_blank.status, BlankStatus.Lost)

    def test_update_date(self):
        blank = BlankInDTO(series="AF", number=1)
        self.crud._create(blank)
        self.crud.update(BlankUpdateDTO(id=1, date=datetime.date(1970, 1, 1)))
        updated_blank = self.crud.get(1)
        self.assertEqual(updated_blank.date, datetime.date(1970, 1, 1))

    def test_update_return(self):
        blank = BlankInDTO(series="AF", number=1)
        self.crud._create(blank)
        self.assertTrue(
            self.crud.update(
                BlankUpdateDTO(id=1, date=datetime.date(1970, 1, 1))
            )
        )
        self.assertFalse(
            self.crud.update(
                BlankUpdateDTO(id=2, date=datetime.date(1970, 1, 1))
            )
        )

    def test_delete(self):
        blank = BlankInDTO(series="AF", number=1)
        cur = self.crud._create(blank)
        self.assertIsNotNone(self.crud.get(1))
        self.crud.delete(1)
        self.assertIsNone(self.crud.get(1))

    def test_delete_return(self):
        blank = BlankInDTO(series="AF", number=1)
        cur = self.crud._create(blank)
        self.assertTrue(self.crud.delete(1))
        self.assertFalse(self.crud.delete(2))