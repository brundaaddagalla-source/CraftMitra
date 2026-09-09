from sqlalchemy.orm import Session

from app.models.user import User
from app.models.buyer_profile import BuyerProfile

from app.schemas.buyer import (
    BuyerCreate,
    BuyerUpdate
)


# -----------------------------------------
# GET BUYER BY ID
# -----------------------------------------

def get_buyer_by_id(
    db: Session,
    buyer_id: int
):
    return (
        db.query(BuyerProfile)
        .filter(BuyerProfile.id == buyer_id)
        .first()
    )


# -----------------------------------------
# GET BUYER BY USER ID
# -----------------------------------------

def get_buyer_by_user_id(
    db: Session,
    user_id: int
):
    return (
        db.query(BuyerProfile)
        .filter(BuyerProfile.user_id == user_id)
        .first()
    )


# -----------------------------------------
# CREATE BUYER PROFILE
# -----------------------------------------

def create_buyer(
    db: Session,
    buyer_data: BuyerCreate
):
    # Check whether user exists
    user = (
        db.query(User)
        .filter(User.id == buyer_data.user_id)
        .first()
    )

    if not user:
        raise ValueError(
            "User does not exist"
        )

    # Check whether buyer profile already exists
    existing_buyer = get_buyer_by_user_id(
        db,
        buyer_data.user_id
    )

    if existing_buyer:
        raise ValueError(
            "This user already has a buyer profile"
        )

    # Create buyer profile
    new_buyer = BuyerProfile(
        user_id=buyer_data.user_id,
        location=buyer_data.location,
        state=buyer_data.state,
        district=buyer_data.district
    )

    db.add(new_buyer)

    db.commit()

    db.refresh(new_buyer)

    return new_buyer


# -----------------------------------------
# UPDATE BUYER PROFILE
# -----------------------------------------

def update_buyer(
    db: Session,
    buyer: BuyerProfile,
    buyer_data: BuyerUpdate
):
    update_data = buyer_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            buyer,
            field,
            value
        )

    db.commit()

    db.refresh(buyer)

    return buyer