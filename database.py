import os
import sqlite3
import logging
from hashlib import md5


logger = logging.getLogger("database")


DB_PATH = os.path.join(os.getcwd(), ".sqlite3")
INIT_SCRIPT_MD5SUM = '9621d88773e62f5c59b26f9cccb74fe1'


def get_connection(db_path=DB_PATH) -> sqlite3.Connection:
    return sqlite3.connect(db_path, autocommit=False)


def init_database(db_path=DB_PATH):
    with open("sql/init.sql", "r") as file:
        init_script = file.read()
        logger.info(f"read {db_path}")
    if md5(init_script.encode()).hexdigest() != INIT_SCRIPT_MD5SUM:
        logger.exception("Init script's sum doesn't equals")
        raise Exception("Invalid init script")
    with get_connection(db_path) as conn:
        conn.executescript(init_script)
        conn.commit()
        logger.info("init database")