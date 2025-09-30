from app.core.security import hash_password, gen_otp, hash_otp
from app.core.exceptions import UserAlreadyExists
from app.domain.interfaces.user_repo import UserRepo
from app.domain.interfaces.token_repo import TokenRepo
from app.domain.interfaces.mailer import Mailer


class RegistrationService:
    def __init__(self, user_repo: UserRepo, token_repo: TokenRepo, mailer: Mailer):
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.mailer = mailer

    def register_user(self, email: str, password: str) -> int:
        if self.user_repo.get_by_email(email):
            raise UserAlreadyExists()

        user_id = self.user_repo.create(email, hash_password(password))
        code = gen_otp()
        self.token_repo.upsert(user_id, hash_otp(code))
        self.mailer.send_code(email, code)
        return user_id
