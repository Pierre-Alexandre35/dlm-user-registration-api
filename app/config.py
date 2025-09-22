from pydantic import BaseModel, Field
import os


class Settings(BaseModel):
    env: str = Field(default=os.getenv("ENV", "local"))
    api_prefix: str = "/v1"

    # Postgres
    pg_dsn: str = Field(default=os.getenv("PG_DSN", "postgresql://app:app@db:5432/app"))

    # SMTP provider (HTTP)
    smtp_base_url: str = Field(
        default=os.getenv("SMTP_BASE_URL", "http://smtp-mock:8080")
    )
    smtp_timeout_s: float = 3.0
    smtp_max_retries: int = 3

    # Security
    argon_time_cost: int = 3
    argon_memory_cost: int = 65536
    argon_parallelism: int = 2

    otp_ttl_seconds: int = 60
    otp_length: int = 4


settings = Settings()
