import os
import sqlite3
import logging
from hashlib import md5
from typing import Callable
from functools import partial


logger = logging.getLogger("database")


# LEGACY:
DB_PATH = os.path.join(os.getcwd(), "..", ".sqlite3")
INIT_SCRIPT_MD5SUM = '9621d88773e62f5c59b26f9cccb74fe1'


def get_connection(db_path: str) -> sqlite3.Connection:
    return sqlite3.connect(db_path, autocommit=False)


def init_database(db_path):
    with open("sql/init.sql", "r") as file:
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