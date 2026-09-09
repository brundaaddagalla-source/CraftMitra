from sqlalchemy.orm import Session

from app.models.buyer_profile import BuyerProfile
from app.models.buyer_address import BuyerAddress

from app.schemas.buyer_address import (
    BuyerAddressCreate,
    BuyerAddressUpdate
)


# -----------------------------------------
# GET ADDRESS BY ID
# -----------------------------------------

def get_address_by_id(
    db: Session,
    address_id: int
):
    return (
        db.query(BuyerAddress)
        .filter(BuyerAddress.id == address_id)
        .first()
    )


# -----------------------------------------
# GET ALL ADDRESSES FOR A BUYER
# -----------------------------------------

def get_addresses_by_buyer_id(
    db: Session,
    buyer_id: int
):
    return (
        db.query(BuyerAddress)
        .filter(BuyerAddress.buyer_id == buyer_id)
        .all()
    )


# -----------------------------------------
# CHECK BUYER EXISTS
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
# REMOVE DEFAULT STATUS FROM OTHER ADDRESSES
# -----------------------------------------

def clear_default_addresses(
    db: Session,
    buyer_id: int
):
    (
        db.query(BuyerAddress)
        .filter(
            BuyerAddress.buyer_id == buyer_id,
            BuyerAddress.is_default == True
        )
        .update(
            {
                BuyerAddress.is_default: False
            },
            synchronize_session=False
        )
    )


# -----------------------------------------
# CREATE BUYER ADDRESS
# -----------------------------------------

def create_address(
    db: Session,
    buyer_id: int,
    address_data: BuyerAddressCreate
):
    # Check whether buyer exists
    buyer = get_buyer_by_id(
        db,
        buyer_id
    )

    if not buyer:
        raise ValueError(
            "Buyer not found"
        )

    # If this is the default address,
    # remove default from existing addresses
    if address_data.is_default:
        clear_default_addresses(
            db,
            buyer_id
        )

    # Create address
    new_address = BuyerAddress(
        buyer_id=buyer_id,
        address_line1=address_data.address_line1,
        address_line2=address_data.address_line2,
        city=address_data.city,
        district=address_data.district,
        state=address_data.state,
        postal_code=address_data.postal_code,
        country=address_data.country,
        is_default=address_data.is_default
    )

    db.add(new_address)

    db.commit()

    db.refresh(new_address)

    return new_address


# -----------------------------------------
# UPDATE BUYER ADDRESS
# -----------------------------------------

def update_address(
    db: Session,
    address: BuyerAddress,
    address_data: BuyerAddressUpdate
):
    update_data = address_data.model_dump(
        exclude_unset=True
    )

    # If this address is being made default,
    # remove default status from other addresses
    if update_data.get("is_default") is True:
        clear_default_addresses(
            db,
            address.buyer_id
        )

    # Update provided fields
    for field, value in update_data.items():
        setattr(
            address,
            field,
            value
        )

    db.commit()

    db.refresh(address)

    return address


# -----------------------------------------
# DELETE BUYER ADDRESS
# -----------------------------------------

def delete_address(
    db: Session,
    address: BuyerAddress
):
    db.delete(address)

    db.commit()