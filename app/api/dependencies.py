from fastapi import Depends
from app.infrastructure.db.cursor import get_db
from app.infrastructure.db.user_repo_pg import PostgresUserRepo
from app.infrastructure.db.token_repo_pg import PostgresTokenRepo
from app.infrastructure.smtp.smtp_client import SmtpMailer
from app.domain.services.registration_service import RegistrationService
from app.domain.services.activation_dispatcher_service import (
    ActivationDispatcherService,
)
from app.domain.services.activation_service import ActivationService


def get_user_repo(conn=Depends(get_db)):
    return PostgresUserRepo(conn)


def get_token_repo(conn=Depends(get_db)):
    return PostgresTokenRepo(conn)


def get_mailer():
    return SmtpMailer()


def get_registration_service(user_repo=Depends(get_user_repo)):
    return RegistrationService(user_repo)


def get_activation_dispatcher_service(
    token_repo=Depends(get_token_repo),
    mailer=Depends(get_mailer),
):
    return ActivationDispatcherService(token_repo, mailer)


def get_activation_service(
    user_repo=Depends(get_user_repo),
    token_repo=Depends(get_token_repo),
):
    return ActivationService(user_repo, token_repo)
