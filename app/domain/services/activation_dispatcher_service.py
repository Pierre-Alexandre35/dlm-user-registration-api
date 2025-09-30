from app.core.security import gen_otp, hash_otp
from app.domain.interfaces.token_repo import TokenRepo
from app.domain.interfaces.mailer import Mailer


# in charge of token generation + mail sending (now RegistrationService is only responsible for user creation.)
class ActivationDispatcherService:
    def __init__(self, token_repo: TokenRepo, mailer: Mailer):
        self.token_repo = token_repo
        self.mailer = mailer

    def dispatch_code(self, user_id: int, email: str) -> None:
        code = gen_otp()
        self.token_repo.upsert(user_id, hash_otp(code))
        self.mailer.send_code(email, code)
