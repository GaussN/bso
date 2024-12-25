import os
import sqlite3
import logging
from hashlib import md5
from typing import Callable
from functools import partial


logger = logging.getLogger("database")


DB_PATH = os.environ["BSO_DB_PATH"]
SQL_PATH = os.environ["BSO_SQL_PATH"]
INIT_SCRIPT_MD5SUM = 'e4c08e6d78a54dff41ea015169b62c1d'


def get_connection(db_path: str) -> sqlite3.Connection:
    return sqlite3.connect(db_path, autocommit=False)


def init_database(db_path: str):
    with open(os.path.join(SQL_PATH, "init.sql"), "r") as file:
        init_script = file.read()
        logger.info(f"read {db_path}")
    init_script_sum = md5(init_script.encode()).hexdigest()
    if init_script_sum != INIT_SCRIPT_MD5SUM:
        logger.exception("Init script's sum doesn't equals")
        logger.debug(f'script sum:"{init_script_sum}"')
        logger.debug(f'should be: "{INIT_SCRIPT_MD5SUM}"')
        raise Exception("Invalid init script")
    with get_connection(db_path) as conn:
        conn.executescript(init_script)
        conn.commit()
        logger.info("init database")