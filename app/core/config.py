import os


class Settings:
    database_url = os.getenv("DATABASE_URL")
    otp_ttl_seconds = int(os.getenv("OTP_TTL_SECONDS", "60"))


settings = Settings()
