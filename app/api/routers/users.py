from fastapi import APIRouter, Depends, HTTPException, status
from app.api.schemas.users import UserCreate, UserIdResponse
from app.core.exceptions import UserAlreadyExists, MailerError
from app.api.dependencies import (
    get_registration_service,
    get_activation_dispatcher_service,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserIdResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    reg_service=Depends(get_registration_service),
    dispatcher=Depends(get_activation_dispatcher_service),
):
    try:
        user_id = reg_service.register_user(payload.email, payload.password)
        dispatcher.dispatch_code(user_id, payload.email)
        return {"id": user_id}
    except UserAlreadyExists:
        raise HTTPException(status_code=409, detail="Email already exists")
    except MailerError:
        raise HTTPException(status_code=503, detail="Could not send activation email")
