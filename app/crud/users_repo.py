from typing import Optional, Iterable
from psycopg import Connection
from psycopg.errors import UniqueViolation


def create_user(conn: Connection, *, email: str, password_hash: str) -> int:
    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (email, password_hash, is_active)
                VALUES (%s, %s, false)
                RETURNING id
                """,
                (email, password_hash),
            )
            return cur.fetchone()["id"]


def get_user_by_id(conn: Connection, user_id: int) -> Optional[dict]:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, email, is_active FROM users WHERE id = %s",
            (user_id,),
        )
        return cur.fetchone()


def list_users(
    conn: Connection, *, limit: int = 50, last_id: int | None = None
) -> Iterable[dict]:
    sql = "SELECT id, email, is_active FROM users"
    params = []
    if last_id is not None:
        sql += " WHERE id > %s"
        params.append(last_id)
    sql += " ORDER BY id LIMIT %s"
    params.append(limit)

    with conn.cursor() as cur:
        cur.execute(sql, tuple(params))
        return cur.fetchall()
