import pytest
from app.domain.services.registration_service import RegistrationService
from app.domain.interfaces.user_repo import UserRepo
from app.domain.interfaces.token_repo import TokenRepo
from app.domain.interfaces.mailer import Mailer
from app.core.exceptions import UserAlreadyExists


class FakeUserRepo(UserRepo):
    def __init__(self):
        self.users = {}

    def create(self, email, pw_hash):
        if email in self.users:
            raise UserAlreadyExists()
        uid = len(self.users) + 1
        self.users[email] = {"id": uid, "hash": pw_hash}
        return uid

    def get_by_email(self, email):
        return self.users.get(email)

    def get_by_id(self, user_id):
        return None

    def activate(self, user_id):
        return True


class FakeTokenRepo(TokenRepo):
    def __init__(self):
        self.tokens = {}

    def upsert(self, user_id, code_hash):
        self.tokens[user_id] = code_hash
        return {"id": 1, "user_id": user_id}

    def get_active_for_user(self, user_id):
        return None

    def consume(self, token_id):
        pass


class FakeMailer(Mailer):
    def __init__(self):
        self.sent = []

    def send_code(self, email, code):
        self.sent.append((email, code))


def test_register_user_sends_email():
    user_repo, token_repo, mailer = FakeUserRepo(), FakeTokenRepo(), FakeMailer()
    service = RegistrationService(user_repo, token_repo, mailer)

    user_id = service.register_user("bob@example.com", "secret")
    assert user_id == 1
    assert mailer.sent[0][0] == "bob@example.com"
    assert len(mailer.sent[0][1]) == 4


def test_register_existing_user_raises():
    user_repo, token_repo, mailer = FakeUserRepo(), FakeTokenRepo(), FakeMailer()
    service = RegistrationService(user_repo, token_repo, mailer)
    service.register_user("bob@example.com", "secret")

    with pytest.raises(UserAlreadyExists):
        service.register_user("bob@example.com", "secret")
