from dataclasses import dataclass
from datetime import datetime


@dataclass
class ActivationToken:
    id: int
    user_id: int
    code_hash: str
    expires_at: datetime
    consumed_at: datetime | None
