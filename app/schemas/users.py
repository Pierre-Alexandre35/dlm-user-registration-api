from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    is_active: bool


class UserIdResponse(BaseModel):
    id: int


class UserListResponse(BaseModel):
    items: List[UserOut]
    next: Optional[int]
