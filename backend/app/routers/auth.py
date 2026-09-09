from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.user import UserResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.auth import (
    LoginRequest,
    TokenResponse
)
from app.services.auth_service import authenticate_user


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# -----------------------------------------
# USER LOGIN
# -----------------------------------------

@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    access_token = authenticate_user(
        db,
        login_data
    )

    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
# -----------------------------------------
# CURRENT AUTHENTICATED USER
# -----------------------------------------

@router.get(
    "/me",
    response_model=UserResponse
)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user