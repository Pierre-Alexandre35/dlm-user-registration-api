from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.api.schemas.tokens import ActivationRequest

from app.api.dependencies import get_activation_service
from app.core.exceptions import InvalidOTP, ExpiredOTP

security = HTTPBasic()
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/activate")
def activate(
    payload: ActivationRequest,
    credentials: HTTPBasicCredentials = Depends(security),
    service=Depends(get_activation_service),
):
    try:
        service.activate(credentials.username, credentials.password, payload.code)
        return {"detail": "Account activated"}
    except InvalidOTP:
        raise HTTPException(status_code=400, detail="Invalid code")
    except ExpiredOTP:
        raise HTTPException(status_code=410, detail="Code expired")
