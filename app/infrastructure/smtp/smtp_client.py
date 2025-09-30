import os
import requests
from app.domain.interfaces.mailer import Mailer
from app.core.exceptions import MailerError

SMTP_URL = os.getenv("SMTP_URL", "http://smtp-mock:8080/send")


class SmtpMailer(Mailer):
    def send_code(self, email: str, code: str) -> None:
        payload = {
            "to": email,
            "subject": "Activation Code",
            "body": f"Your activation code is {code}",
        }
        try:
            resp = requests.post(SMTP_URL, json=payload, timeout=5)
            resp.raise_for_status()
        except requests.RequestException as e:
            raise MailerError(f"Failed to send email to {email}: {e}") from e
