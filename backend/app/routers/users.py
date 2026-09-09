from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.models.user import User
from app.database import get_db
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse
)

from app.services import user_service


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


# -----------------------------------------
# CREATE USER
# -----------------------------------------

@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    try:
        user = user_service.create_user(
            db,
            user_data
        )

        return user

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


# -----------------------------------------
# GET USER BY ID
# -----------------------------------------
@router.get(
    "/{user_id}",
    response_model=UserResponse
)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own account"
        )

    return current_user


# -----------------------------------------
# UPDATE USER
# -----------------------------------------

@router.patch(
    "/{user_id}",
    response_model=UserResponse
)
def update_existing_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Ownership check
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own account"
        )

    updated_user = user_service.update_user(
        db,
        current_user,
        user_data
    )

    return updated_user