# tests/test_auth.py

import pytest
from datetime import datetime, timedelta, timezone
from app.crud.tokens_repo import TokensRepo


@pytest.fixture
def repo():
    return TokensRepo()


def test_upsert_for_user(mocker, repo):
    conn = mocker.MagicMock()
    cursor = conn.cursor.return_value.__enter__.return_value
    expected_token = {
        "id": 1,
        "user_id": 42,
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(seconds=60),
    }
    cursor.fetchone.return_value = expected_token

    result = repo.upsert_for_user(conn, user_id=42, code_hash="hash123")

    assert result == expected_token

    # Assert DELETE was called first
    assert any(
        "DELETE FROM activation_tokens" in call.args[0]
        for call in cursor.execute.call_args_list
    )

    # Assert INSERT was called
    assert any(
        "INSERT INTO activation_tokens" in call.args[0]
        for call in cursor.execute.call_args_list
    )


def test_get_active_for_user(mocker, repo):
    conn = mocker.MagicMock()
    cursor = conn.cursor.return_value.__enter__.return_value
    expected_token = {
        "id": 1,
        "user_id": 42,
        "created_at": datetime.now(timezone.utc),
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=1),
    }
    cursor.fetchone.return_value = expected_token

    result = repo.get_active_for_user(conn, user_id=42)

    assert result == expected_token
    assert "SELECT * FROM activation_tokens" in cursor.execute.call_args[0][0]
    assert (42,) == cursor.execute.call_args[0][1]


def test_consume_token(mocker, repo):
    conn = mocker.MagicMock()
    cursor = conn.cursor.return_value.__enter__.return_value

    repo.consume(conn, token_id=123)

    assert (
        "UPDATE activation_tokens SET consumed_at = now()"
        in cursor.execute.call_args[0][0]
    )
    assert (123,) == cursor.execute.call_args[0][1]
