import secrets
import hmac
from argon2 import PasswordHasher

ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=2)


def hash_password(pw: str) -> str:
    return ph.hash(pw)


def verify_password(hash_: str, pw: str) -> bool:
    try:
        ph.verify(hash_, pw)
        return True
    except Exception:
        return False


def gen_otp(n_digits: int = 4) -> str:
    # cryptographically random 4-digit code with leading zeros allowed
    return f"{secrets.randbelow(10**n_digits):0{n_digits}d}"


def hash_otp(code: str) -> str:
    # Argon2 on the 4-digit code is acceptable to mitigate brute-force if DB leaks
    return ph.hash(code)


def constant_time_eq(a: str, b: str) -> bool:
    return hmac.compare_digest(a, b)
