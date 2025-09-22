# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from psycopg import Connection
from psycopg.errors import UniqueViolation

from app.core.security import hash_password
from app.db.cursor import get_db
from app.schemas.users import UserCreate, UserOut, UserIdResponse
from app.crud import users_repo

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserIdResponse, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, conn: Connection = Depends(get_db)):
    try:
        pw_hash = hash_password(payload.password)  # <-- hash here
        new_id = users_repo.create_user(
            conn, email=payload.email, password_hash=pw_hash
        )
        return {"id": new_id}
    except UniqueViolation:
        raise HTTPException(status_code=409, detail="Email already exists")
