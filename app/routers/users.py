from fastapi import APIRouter, Depends, HTTPException, Query
from psycopg import Connection
from psycopg.errors import UniqueViolation

from app.db.cursor import get_db
from app.schemas.users import UserCreate, UserOut, UserIdResponse, UserListResponse
from app.crud import users_repo


router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserIdResponse)
def create_user(payload: UserCreate, conn: Connection = Depends(get_db)):
    try:
        new_id = users_repo.create_user(
            conn, email=payload.email, password_hash=payload.password_hash
        )
        return {"id": new_id}
    except UniqueViolation:
        raise HTTPException(status_code=409, detail="Email already exists")


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, conn: Connection = Depends(get_db)):
    row = users_repo.get_user_by_id(conn, user_id)
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return row


@router.get("", response_model=UserListResponse)
def list_users(
    limit: int = Query(50, ge=1, le=200),
    last_id: int | None = Query(None, ge=0),
    conn: Connection = Depends(get_db),
):
    rows = users_repo.list_users(conn, limit=limit, last_id=last_id)
    next_cursor = rows[-1]["id"] if rows else None
    return {"items": rows, "next": next_cursor}
