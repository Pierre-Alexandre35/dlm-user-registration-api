import httpx
from app.config import settings


def send_code_email(to_email: str, code: str) -> None:
    with httpx.Client(
        base_url=settings.smtp_base_url, timeout=settings.smtp_timeout_s
    ) as c:
        for attempt in range(settings.smtp_max_retries):
            try:
                r = c.post(
                    "/send",
                    json={
                        "to": to_email,
                        "subject": "Your code",
                        "body": f"Code: {code}",
                    },
                )
                r.raise_for_status()
                return
            except Exception:
                if attempt + 1 == settings.smtp_max_retries:
                    raise
