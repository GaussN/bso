import logging
import sqlite3
import datetime as dt

from abc import ABC
from typing import Callable, Optional, Any, Iterable

import blanks.models as models


class BlankAdapter(ABC):
    __date_format = "%Y-%m-%d %H:%M:%S"

    @staticmethod
    def strftime(date: dt.date) -> str:
        return date.strftime(BlankAdapter.__date_format)

    @staticmethod
    def to_dict(blank: models.BlankInDTO) -> dict:
        dict_ = blank.__dict__
        if isinstance(date := dict_["date"], dt.date):
            dict_["date"] = date.strftime(BlankAdapter.__date_format)
        if isinstance(status := dict_["status"], models.BlankStatus):
            dict_["status"] = status.value
        return dict_

    @staticmethod
    def from_dict(dict_: dict) -> models.BlankOutDTO:
        if not dict_:
            return None
        for date_field in ("date", "created_at", "updated_at", "deleted_at"):
            date = dict_.get(date_field)
            if isinstance(date, str):
                dict_[date_field] = dt.datetime.strptime(date, BlankAdapter.__date_format)
        date = dict_.get("date")
        status = dict_.get("status")
        if status is not None and isinstance(status, int):
            dict_["status"] = models.BlankStatus(status)
        return models.BlankOutDTO(**dict_)


class _BlankCRUD_utils(ABC):
    def _get_insert_stmt_from_range(self, range_: models.BlankRangeInDTO) -> tuple[str, list[tuple]]:
        query = "INSERT INTO blanks(series, number) VALUES(?, ?)"
        params = [(range_.series, n) for n in range_.get_range()]
        return query, params


    def _get_update_stmt(self, blank_update: models.BlankUpdateDTO) -> tuple[str, tuple]:
        blank_updates_dict = BlankAdapter.to_dict(blank_update)  # noqa
        params = []
        def _(k, v):
            params.append(v)
            return f"{k}=?"
        sets = ",".join((_(k, v) for k,v in blank_updates_dict.items() if not isinstance(v, models.Undefined)  and k != "id"))
        return (
            (f"UPDATE blanks SET {sets},updated_at=datetime('now') WHERE id=? RETURNING id"), 
            (*params, blank_update.id)
        )

    
    def execute(self, query: str, params: Iterable | dict = tuple()):
        self._logger.log(15, f"{query=}")
        self._logger.log(15, f"{params=}")
        try:
            if isinstance(params, list):
                cursor = self._connection.executemany(query, params)    
            else: 
                cursor = self._connection.execute(query, params)
            cursor.row_factory = sqlite3.Row
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
        self._logger.info(f"{self._id}.__init__")
        

    def __del__(self):
        self._logger.info(f"{self._id}.__del__")
        self._connection.close()


    def create_from_range(self, range_: models.BlankRangeInDTO) -> sqlite3.Cursor:
        return self.execute(*self._get_insert_stmt_from_range(range_))


    def _create(self, blanks: models.BlankInDTO | list[models.BlankInDTO]) -> sqlite3.Cursor:
        """ONLY FOR TESTS"""
        query = (
            "INSERT INTO blanks(date, series, number, comment, status) " 
            "VALUES(:date, :series, :number, :comment, :status) "
        )
        if isinstance(blanks, list):
            return self.execute(query, [BlankAdapter.to_dict(i) for i in blanks])
        return self.execute(query, BlankAdapter.to_dict(blanks))   


    def read_with_filter(self, raw_filter: str = "", params: Iterable | dict = tuple()) -> list[models.BlankOutDTO]:
        query = "SELECT * FROM c_blanks"
        if raw_filter:
            query += f" {raw_filter}"
        cur = self.execute(query, params)
        return [BlankAdapter.from_dict(dict(i)) for i in cur]


    def read(self) -> list[models.BlankOutDTO]:
        return self.read_with_filter()


    def get(self, id: int) -> Optional[models.BlankOutDTO]:
        query = "SELECT * FROM c_blanks WHERE id = ?"
        cur = self.execute(query, (id,))
        return BlankAdapter.from_dict(dict(cur.fetchone() or {}))


    def update(self, updates: models.BlankUpdateDTO) -> bool:
        _ = self.execute(*self._get_update_stmt(updates)).fetchone()
        return not not _


    def delete(self, id: int) -> bool:
        query = "UPDATE blanks SET updated_at=datetime('now'),deleted_at=datetime('now') WHERE id=? RETURNING id"
        _ = self.execute(query, (id,)).fetchone()
        return not not _
        