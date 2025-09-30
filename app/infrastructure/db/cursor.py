from psycopg_pool import ConnectionPool
from psycopg.rows import dict_row
from psycopg import Connection
from typing import Generator
from app.core.config import settings

pool = ConnectionPool(conninfo=settings.database_url, kwargs={"autocommit": False})


def get_db() -> Generator[Connection, None, None]:
    with pool.connection() as conn:
        conn.row_factory = dict_row
        yield conn
