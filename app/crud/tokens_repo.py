# crud/tokens_repo.py
from typing import Optional
from datetime import datetime, timedelta, timezone
from app.config import settings
from psycopg import Connection
from app.db.cursor import get_db


class TokensRepo:
    def upsert_for_user(self, conn: Connection, user_id: int, code_hash: str) -> dict:
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=settings.otp_ttl_seconds
        )
        with conn.transaction():
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM activation_tokens WHERE user_id = %s AND consumed_at IS NULL",
                    (user_id,),
                )
                cur.execute(
                    """INSERT INTO activation_tokens (user_id, code_hash, expires_at)
                       VALUES (%s, %s, %s)
                       RETURNING id, user_id, created_at, expires_at""",
                    (user_id, code_hash, expires_at),
                )
                return cur.fetchone()

    def get_active_for_user(self, conn: Connection, user_id: int) -> Optional[dict]:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT * FROM activation_tokens
                           WHERE user_id = %s AND consumed_at IS NULL
                           ORDER BY created_at DESC LIMIT 1""",
                (user_id,),
            )
            return cur.fetchone()

    def consume(self, conn: Connection, token_id: int) -> None:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE activation_tokens SET consumed_at = now() WHERE id = %s",
                (token_id,),
            )
