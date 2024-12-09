import sqlite3
from typing import Callable

from models import BlankDTO


class BlankCRUD:
    def __init__(self, get_connection: Callable[[], sqlite3.Connection]):
        self.__get_connection = get_connection

    @staticmethod
    def __add_connection(func):
        def _(self, *args, **kwargs):
            try:
                setattr(self, "conn", self.__get_connection())
                func(*args, **kwargs)
            except sqlite3.IntegrityError as ie:
                ...
            finally:
                self.conn.close()    
        return _

    @BlankCRUD.__add_connection
    def create_range(self, _: ...):
        ...

    @BlankCRUD.__add_connection
    def create(self, blank: BlankDTO):
        ...

    @BlankCRUD.__add_connection
    def read(self, _: ...):
        ...

    @BlankCRUD.__add_connection
    def update(self, _: ...):
        ...

    @BlankCRUD.__add_connection
    def delete(self, _: ...):
        ...