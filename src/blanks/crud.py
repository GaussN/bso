import logging
import sqlite3
import datetime as dt

from abc import ABC
from typing import Callable, Optional, Any, Iterable

import blanks.models as models


class BlankAdapter(ABC):
    __date_format = "%Y-%m-%d %H:%M:%S"

    @staticmethod
    def to_dict(blank: models.BlankInDTO) -> dict:
        d = blank.__dict__
        if date := d["date"]:
            d["date"] = date.strftime(BlankAdapter.__date_format)
        return d

    @staticmethod
    def from_dict(d: dict) -> models.BlankOutDTO:
        if not d:
            return None
        for k, v in d.items():
            if isinstance(v, dt.date):
                d[k] = v.strftime(BlankAdapter.__date_format)
        return models.BlankOutDTO(**d)


class _BlankCRUD_utils(ABC):
    def _get_insert_stmt_from_range(self, range_: models.BlankRangeInDTO) -> tuple[str, list[tuple]]:
        query = "INSERT INTO blanks(series, number) VALUES(?, ?)"
        params = [(range_.series, n) for n in range_.get_range()]
        return query, params


    def _get_update_stmt(self, blank_update: models.BlankUpdateDTO) -> tuple[str, tuple]:
        if isinstance(blank_update.status, models.BlankState):
            blank_update.status = blank_update.status.value  # WARNING: cs
        params = []
        def _(k, v):
            params.append(v)
            return f"{k}=?"
        sets = ",".join((_(k, v) for k,v in blank_update.__dict__.items() if v and k != "id"))
        return f"UPDATE blanks SET {sets},updated_at=datetime('now') WHERE id=?", (*params, blank_update.id) 

    
    def execute(self, query: str, params: Iterable | dict = tuple(), *, commit: bool = True):
        try:
            if isinstance(params, list):
                cursor = self._connection.executemany(query, params)    
            else: 
                cursor = self._connection.execute(query, params)
            cursor.row_factory = sqlite3.Row
            if commit:
                self._connection.commit()
            return cursor
        except sqlite3.IntegrityError as ie:
            self._logger.error(ie)
            self._connection.rollback()
            raise
            

class BlankCRUD(_BlankCRUD_utils):
    def __init__(self, get_connection: Callable[[], sqlite3.Connection]):
        self._connection = get_connection()
        self._logger = logging.getLogger("blanks.CRUD")
        self._id = hex(id(self))
        self._logger.debug(f"{self._id}.__init__")
        

    def __del__(self):
        self._logger.debug(f"{self._id}.__del__")
        self._connection.close()


    def create_from_range(self, range_: models.BlankRangeInDTO) -> sqlite3.Cursor:
        return self.execute(*self._get_insert_stmt_from_range(range_), commit=True)


    def create(self, blanks: models.BlankInDTO | list[models.BlankInDTO]) -> sqlite3.Cursor:
        """NOT USED"""
        query = (
            "INSERT INTO blanks(date, series, number, comment, status) " 
            "VALUES(:date, :series, :number, :comment, :status) "
        )
        if isinstance(blanks, list):
            return self.execute(query, [BlankAdapter.to_dict(i) for i in blanks])
        return self.execute(query, BlankAdapter.to_dict(blanks))   


    def read_with_filter(self, raw_filter: str = "", params: Iterable | dict = tuple()) -> list[models.BlankOutDTO]:
        query = "SELECT * FROM blanks"
        if raw_filter:
            query += f" {raw_filter}"
        cur = self.execute(query, params, commit=False)
        return [BlankAdapter.from_dict(dict(i)) for i in cur]


    def read(self) -> list[models.BlankOutDTO]:
        return self.read_with_filter()


    def get(self, id: int) -> Optional[models.BlankOutDTO]:
        query = "SELECT * FROM blanks WHERE id = ?"
        cur = self.execute(query, (id,), commit=False)
        return BlankAdapter.from_dict(dict(cur.fetchone() or {}))


    def update(self, updates: models.BlankUpdateDTO) -> sqlite3.Cursor:
        return self.execute(*self._get_update_stmt(updates), commit=True)


    def delete(self, id: int) -> sqlite3.Cursor:
        query = "UPDATE blanks SET updated_at=datetime('now'),deleted_at=datetime('now') WHERE id=?"
        return self.execute(query, (id,), commit=True)
        