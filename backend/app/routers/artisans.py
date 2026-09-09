from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from app.core.dependencies import (
    get_current_user,
    require_artisan
)

from app.models.user import User
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.artisan import (
    ArtisanCreate,
    ArtisanUpdate,
    ArtisanResponse
)

from app.services import artisan_service


router = APIRouter(
    prefix="/artisans",
    tags=["Artisans"]
)


# -----------------------------------------
# CREATE ARTISAN PROFILE
# -----------------------------------------
@router.post(
    "",
    response_model=ArtisanResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_artisan(
    artisan_data: ArtisanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_artisan)
):
    # Ensure the artisan can only create
    # a profile linked to their own account
    if artisan_data.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only create an artisan profile for your own account"
        )

    try:
        artisan = artisan_service.create_artisan(
            db,
            artisan_data
        )

        return artisan

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )

# -----------------------------------------
# GET ARTISAN BY ID
# -----------------------------------------

@router.get(
    "/{artisan_id}",
    response_model=ArtisanResponse
)
def get_artisan(
    artisan_id: int,
    db: Session = Depends(get_db)
):
    artisan = artisan_service.get_artisan_by_id(
        db,
        artisan_id
    )

    if not artisan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artisan not found"
        )

    return artisan


# -----------------------------------------
# UPDATE ARTISAN PROFILE
# -----------------------------------------
@router.patch(
    "/{artisan_id}",
    response_model=ArtisanResponse
)
def update_existing_artisan(
    artisan_id: int,
    artisan_data: ArtisanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_artisan)
):
    artisan = artisan_service.get_artisan_by_id(
        db,
        artisan_id
    )

    if not artisan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Artisan not found"
        )

    # Ownership check
    if artisan.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own artisan profile"
        )

    updated_artisan = artisan_service.update_artisan(
        db,
        artisan,
        artisan_data
    )

    return updated_artisan