from datetime import datetime, timezone
from app.core.security import verify_password
from app.core.exceptions import InvalidOTP, ExpiredOTP
from app.domain.interfaces.user_repo import UserRepo
from app.domain.interfaces.token_repo import TokenRepo


class ActivationService:
    def __init__(self, user_repo: UserRepo, token_repo: TokenRepo):
        self.user_repo = user_repo
        self.token_repo = token_repo

    def activate(self, email: str, password: str, code: str) -> None:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(user.password_hash, password):
            raise InvalidOTP("Bad credentials")

        token = self.token_repo.get_active_for_user(user.id)
        if not token:
            raise InvalidOTP("No active token")

        if datetime.now(timezone.utc) > token.expires_at:
            raise ExpiredOTP()

        if not verify_password(token.code_hash, code):
            raise InvalidOTP()

        self.token_repo.consume(token.id)
        self.user_repo.activate(user.id)
