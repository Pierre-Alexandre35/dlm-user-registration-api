from pydantic import BaseModel


class ActivationRequest(BaseModel):
    code: str


class TokenOut(BaseModel):
    id: int
    user_id: int
    expires_at: str
