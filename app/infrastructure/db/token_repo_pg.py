from datetime import datetime, timedelta, timezone
from app.core.config import settings
from app.domain.entities.token import ActivationToken
from app.domain.interfaces.token_repo import TokenRepo
from psycopg import Connection


class PostgresTokenRepo(TokenRepo):
    def __init__(self, conn: Connection):
        self.conn = conn

    def upsert(self, user_id: int, code_hash: str) -> ActivationToken:
        expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=settings.otp_ttl_seconds
        )
        with self.conn.transaction():
            with self.conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM activation_tokens WHERE user_id = %s AND consumed_at IS NULL",
                    (user_id,),
                )
                cur.execute(
                    """
                    INSERT INTO activation_tokens (user_id, code_hash, expires_at)
                    VALUES (%s, %s, %s)
                    RETURNING id, user_id, code_hash, expires_at, consumed_at
                    """,
                    (user_id, code_hash, expires_at),
                )
                row = cur.fetchone()
                return ActivationToken(**row)
