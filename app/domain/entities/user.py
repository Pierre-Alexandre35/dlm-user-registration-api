from dataclasses import dataclass


@dataclass
class User:
    id: int
    email: str
    is_active: bool
    password_hash: str
