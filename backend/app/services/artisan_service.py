from sqlalchemy.orm import Session

from app.models.user import User
from app.models.artisan_profile import ArtisanProfile

from app.schemas.artisan import (
    ArtisanCreate,
    ArtisanUpdate
)


# -----------------------------------------
# GET ARTISAN BY ID
# -----------------------------------------

def get_artisan_by_id(
    db: Session,
    artisan_id: int
):
    return (
        db.query(ArtisanProfile)
        .filter(ArtisanProfile.id == artisan_id)
        .first()
    )


# -----------------------------------------
# GET ARTISAN BY USER ID
# -----------------------------------------

def get_artisan_by_user_id(
    db: Session,
    user_id: int
):
    return (
        db.query(ArtisanProfile)
        .filter(ArtisanProfile.user_id == user_id)
        .first()
    )


# -----------------------------------------
# CREATE ARTISAN PROFILE
# -----------------------------------------

def create_artisan(
    db: Session,
    artisan_data: ArtisanCreate
):
    # Check whether the user exists
    user = (
        db.query(User)
        .filter(User.id == artisan_data.user_id)
        .first()
    )

    if not user:
        raise ValueError(
            "User does not exist"
        )

    # Check whether this user already
    # has an artisan profile
    existing_artisan = get_artisan_by_user_id(
        db,
        artisan_data.user_id
    )

    if existing_artisan:
        raise ValueError(
            "This user already has an artisan profile"
        )

    # Create artisan profile
    new_artisan = ArtisanProfile(
        user_id=artisan_data.user_id,
        location=artisan_data.location,
        state=artisan_data.state,
        district=artisan_data.district,
        preferred_language=artisan_data.preferred_language,
        craft_type=artisan_data.craft_type,
        profile_image=artisan_data.profile_image
    )

    db.add(new_artisan)

    db.commit()

    db.refresh(new_artisan)

    return new_artisan


# -----------------------------------------
# UPDATE ARTISAN PROFILE
# -----------------------------------------

def update_artisan(
    db: Session,
    artisan: ArtisanProfile,
    artisan_data: ArtisanUpdate
):
    update_data = artisan_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            artisan,
            field,
            value
        )

    db.commit()

    db.refresh(artisan)

    return artisan