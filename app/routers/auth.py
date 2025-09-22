# app/routers/auth.py
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, EmailStr, Field
from psycopg import Connection

from app.config import settings
from app.core.security import hash_password, gen_otp, hash_otp, ph
from app.crud import users_repo
from app.crud.tokens_repo import TokensRepo
from app.db.cursor import get_db
from app.services.smtp_client import send_code_email
from psycopg.errors import UniqueViolation

router = APIRouter(prefix="/auth", tags=["auth"])
basic = HTTPBasic()
tokens = TokensRepo()


# --- Request models ---
class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class EmailIn(BaseModel):
    email: EmailStr


# --- Routes ---
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, conn: Connection = Depends(get_db)):
    pw_hash = hash_password(payload.password)
    try:
        new_id = users_repo.create_user(
            conn, email=payload.email, password_hash=pw_hash
        )
    except UniqueViolation:
        raise HTTPException(status_code=409, detail="Email already exists")
    return {"id": new_id}


@router.post("/send-activation", status_code=status.HTTP_202_ACCEPTED)
def send_activation(payload: EmailIn, conn: Connection = Depends(get_db)):
    user = users_repo.get_user_by_email(conn, payload.email)
    if user:
        code = gen_otp(settings.otp_length)
        code_hash = hash_otp(code)
        tokens.upsert_for_user(conn, user["id"], code_hash)  # ✅ pass conn
        send_code_email(payload.email, code)
    return {"status": "sent"}


@router.post("/activate")
def activate(
    credentials: HTTPBasicCredentials = Depends(basic),
    conn: Connection = Depends(get_db),
):
    # BASIC AUTH: username=email, password=4-digit code
    email, code = credentials.username, credentials.password
    user = users_repo.get_user_by_email(conn, email)
    if not user:
        # keep error generic to avoid oracle behavior
        raise HTTPException(status_code=401, detail="Invalid credentials")

    tok = tokens.get_active_for_user(conn, user["id"])
    if not tok:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if datetime.now(timezone.utc) > tok["expires_at"]:
        raise HTTPException(status_code=410, detail="Code expired")

    try:
        ph.verify(tok["code_hash"], code)  # Argon2 verify
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    tokens.consume(conn, tok["id"])
    users_repo.activate_user(conn, user["id"])
    return {"status": "activated"}
