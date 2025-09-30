# app/core/config.py
import os


class Settings:
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL", "postgresql://app:app@postgres:5432/app"
    )

    # OTP
    otp_ttl_seconds: int = int(os.getenv("OTP_TTL_SECONDS", "60"))
    otp_length: int = int(os.getenv("OTP_LENGTH", "4"))

    # SMTP
    smtp_url: str = os.getenv("SMTP_URL", "http://smtp-mock:8080/send")
    smtp_timeout: int = int(os.getenv("SMTP_TIMEOUT", "5"))
    smtp_max_retries: int = int(os.getenv("SMTP_MAX_RETRIES", "3"))


settings = Settings()
