from app.core.security import hash_password
from app.core.exceptions import UserAlreadyExists
from app.domain.interfaces.user_repo import UserRepo


class RegistrationService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    def register_user(self, email: str, password: str) -> int:
        if self.user_repo.get_by_email(email):
            raise UserAlreadyExists()
        return self.user_repo.create(email, hash_password(password))
