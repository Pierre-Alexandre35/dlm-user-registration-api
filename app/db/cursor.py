# app/db.py
import os
import psycopg
from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from psycopg import Connection
from typing import Generator

DB_DSN = os.getenv("DATABASE_URL")

pool = ConnectionPool(
    conninfo=DB_DSN,
    min_size=5,
    max_size=20,
    max_idle=10,
    timeout=5,
    kwargs={"autocommit": False},
)


def get_db() -> Generator[Connection, None, None]:
    with pool.connection() as conn:
        conn.row_factory = dict_row
        yield conn
