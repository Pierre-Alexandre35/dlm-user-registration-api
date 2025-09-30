import os
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from psycopg import Connection
from typing import Generator

pool = ConnectionPool(conninfo=os.getenv("DATABASE_URL"), kwargs={"autocommit": False})


def get_db() -> Generator[Connection, None, None]:
    with pool.connection() as conn:
        conn.row_factory = dict_row
        yield conn
