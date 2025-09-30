import pytest
from psycopg import connect
from app.infrastructure.db.user_repo_pg import PostgresUserRepo
from app.core.exceptions import UserAlreadyExists


@pytest.fixture
def conn():
    dsn = "postgresql://app:secret@localhost:5432/test_app"
    with connect(dsn, autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("DROP TABLE IF EXISTS users CASCADE;")
            cur.execute(
                """
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    is_active BOOLEAN NOT NULL DEFAULT false
                )
            """
            )
        yield conn


def test_create_user_and_unique_violation(conn):
    repo = PostgresUserRepo(conn)
    user_id = repo.create("alice@example.com", "hash")
    assert isinstance(user_id, int)

    with pytest.raises(UserAlreadyExists):
        repo.create("alice@example.com", "hash")
