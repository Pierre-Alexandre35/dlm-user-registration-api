import pytest
from datetime import datetime, timedelta, timezone
from app.domain.services.activation_service import ActivationService
from app.core.exceptions import InvalidOTP, ExpiredOTP
from app.domain.entities.user import User
from app.domain.entities.token import ActivationToken


class FakeUserRepo:
    def __init__(self, user):
        self.user = user

    def get_by_email(self, email):
        return self.user

    def activate(self, user_id):
        self.user.is_active = True
        return True


class FakeTokenRepo:
    def __init__(self, token):
        self.token = token
        self.consumed = False

    def get_active_for_user(self, user_id):
        return None if self.consumed else self.token

    def consume(self, token_id):
        self.consumed = True


def test_activation_invalid_password():
    user = User(id=1, email="u@example.com", is_active=False, password_hash="bad")
    service = ActivationService(FakeUserRepo(user), FakeTokenRepo(None))
    with pytest.raises(InvalidOTP):
        service.activate("u@example.com", "wrongpw", "1234")


def test_activation_expired_token(monkeypatch):
    user = User(id=1, email="u@example.com", is_active=False, password_hash="hash")
    expired = ActivationToken(
        id=1,
        user_id=1,
        code_hash="hash",
        expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
        consumed_at=None,
    )
    service = ActivationService(FakeUserRepo(user), FakeTokenRepo(expired))

    # Patch password check to succeed so we can test expiry logic
    monkeypatch.setattr(
        "app.domain.services.activation_service.verify_password", lambda h, pw: True
    )

    with pytest.raises(ExpiredOTP):
        service.activate("u@example.com", "hash", "1234")


def test_activation_happy_path(monkeypatch):
    user = User(id=1, email="u@example.com", is_active=False, password_hash="hash")
    valid = ActivationToken(
        id=1,
        user_id=1,
        code_hash="hash",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=1),
        consumed_at=None,
    )
    service = ActivationService(FakeUserRepo(user), FakeTokenRepo(valid))

    # Patch verify_password to always succeed
    monkeypatch.setattr(
        "app.domain.services.activation_service.verify_password", lambda h, pw: True
    )

    service.activate("u@example.com", "hash", "1234")
    assert user.is_active
