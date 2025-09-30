import pytest
from psycopg import connect
from datetime import datetime, timedelta, timezone
from app.infrastructure.db.token_repo_pg import PostgresTokenRepo


@pytest.fixture
def conn():
    dsn = "postgresql://app:secret@localhost:5432/test_app"
    with connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS activation_tokens CASCADE;")
            cur.execute(
                """
                CREATE TABLE activation_tokens (
                    id SERIAL PRIMARY KEY,
                    user_id INT NOT NULL,
                    code_hash TEXT NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                    expires_at TIMESTAMPTZ NOT NULL,
                    consumed_at TIMESTAMPTZ
                )
            """
            )
        yield conn


def test_upsert_and_consume(conn):
    repo = PostgresTokenRepo(conn)
    token = repo.upsert(1, "hash")
    assert token.user_id == 1

    active = repo.get_active_for_user(1)
    assert active is not None

    repo.consume(active.id)
    consumed = repo.get_active_for_user(1)
    assert consumed is None
