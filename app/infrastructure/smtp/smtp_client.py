import requests
from app.domain.interfaces.mailer import Mailer
from app.core.exceptions import MailerError
from app.core.config import settings


class SmtpMailer(Mailer):
    def send_code(self, email: str, code: str) -> None:
        payload = {
            "to": email,
            "subject": "Activation Code",
            "body": f"Your activation code is {code}",
        }

        for attempt in range(settings.smtp_max_retries):
            try:
                resp = requests.post(
                    settings.smtp_url,
                    json=payload,
                    timeout=settings.smtp_timeout,
                )
                resp.raise_for_status()
                return
            except requests.RequestException as e:
                if attempt + 1 == settings.smtp_max_retries:
                    raise MailerError(f"Failed to send email to {email}: {e}") from e
