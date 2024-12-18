import logging
import sqlite3
import datetime as dt
from abc import ABC
from typing import Callable, Optional, Any

from src.web.models import BlankInDTO, BlankOutDTO, BlankUpdateDTO


class BlankAdapter(ABC):
    __date_format = "%Y-%m-%d %H:%M:%S"

    @staticmethod
    def to_dict(blank: BlankInDTO) -> dict:
        d = blank.__dict__
        if date := d["date"]:
            d["date"] = date.strftime(BlankAdapter.__date_format)
        return d

    @staticmethod
    def from_dict(d: dict) -> BlankOutDTO:
        if not d:
            return None
        for k, v in d.items():
            if isinstance(v, dt.date):
                d[k] = v.strftime(BlankAdapter.__date_format)
        return BlankOutDTO(**d)


class _BlankCRUD_utils(ABC):
    def execute(self, query: str, params: tuple | list = tuple(), *, commit: bool = True):
        try:
            if isinstance(params, list):
                cursor = self._connection.executemany(query, params)    
            else: 
                cursor = self._connection.execute(query, params)
            cursor.row_factory = sqlite3.Row
            if commit:
                self._connection.commit()
            return cursor
        # FIXME: 
        except Exception:
            self._connection.rollback()
            raise
            

class BlankCRUD(_BlankCRUD_utils):
    def __init__(self, get_connection: Callable[[], sqlite3.Connection]):
        self._connection = get_connection()
        self._logger = logging.getLogger("blanks.CRUD")


    def __del__(self):
        self._connection.close()


    def create(self, blanks: BlankInDTO | list[BlankInDTO]) -> sqlite3.Cursor:
        self._logger.debug(f"create:\n{blanks}")
        query = (
            "INSERT INTO blanks(date, series, number, comment, status) " 
            "VALUES(:date, :series, :number, :comment, :status) "
        )
        if isinstance(blanks, list):
            return self.execute(query, [BlankAdapter.to_dict(i) for i in blanks])
        return self.execute(query, BlankAdapter.to_dict(blanks))
        

    def read(self) -> list[BlankOutDTO]:
        query = "SELECT * FROM blanks"
        cur = self.execute(query, commit=False)
        return [BlankAdapter.from_dict(dict(i)) for i in cur]


    def get(self, id: int) -> Optional[BlankOutDTO]:
        self._logger.debug(f"get {id}")
        query = "SELECT * FROM blanks WHERE id = ?"
        cur = self.execute(query, (id,), commit=False)
        return BlankAdapter.from_dict(dict(cur.fetchone() or {}))


    def update(self, updates: BlankUpdateDTO) -> sqlite3.Cursor:
        query, params = updates.get_update_stmt()
        self._logger.debug(f"update {updates} with {query}")       
        return self.execute(query, params, commit=True)


    def delete(self, id: int) -> sqlite3.Cursor:
        self._logger.debug(f"delete {id}")
        query = "UPDATE blanks SET updated_at=datetime('now'),deleted_at=datetime('now') WHERE id=?"
        return self.execute(query, (id,), commit=True)
        