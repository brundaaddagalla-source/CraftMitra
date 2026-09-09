from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from app.schemas.buyer_address import (
    BuyerAddressCreate,
    BuyerAddressUpdate,
    BuyerAddressResponse
)
from app.services import buyer_address_service

from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.buyer import (
    BuyerCreate,
    BuyerUpdate,
    BuyerResponse
)

from app.services import buyer_service


router = APIRouter(
    prefix="/buyers",
    tags=["Buyers"]
)


# -----------------------------------------
# CREATE BUYER PROFILE
# -----------------------------------------

@router.post(
    "",
    response_model=BuyerResponse,
    status_code=status.HTTP_201_CREATED
)
def create_new_buyer(
    buyer_data: BuyerCreate,
    db: Session = Depends(get_db)
):
    try:
        buyer = buyer_service.create_buyer(
            db,
            buyer_data
        )

        return buyer

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


# -----------------------------------------
# GET BUYER BY ID
# -----------------------------------------

@router.get(
    "/{buyer_id}",
    response_model=BuyerResponse
)
def get_buyer(
    buyer_id: int,
    db: Session = Depends(get_db)
):
    buyer = buyer_service.get_buyer_by_id(
        db,
        buyer_id
    )

    if not buyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buyer not found"
        )

    return buyer


# -----------------------------------------
# UPDATE BUYER PROFILE
# -----------------------------------------

@router.patch(
    "/{buyer_id}",
    response_model=BuyerResponse
)
def update_existing_buyer(
    buyer_id: int,
    buyer_data: BuyerUpdate,
    db: Session = Depends(get_db)
):
    buyer = buyer_service.get_buyer_by_id(
        db,
        buyer_id
    )

    if not buyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buyer not found"
        )

    updated_buyer = buyer_service.update_buyer(
        db,
        buyer,
        buyer_data
    )

    return updated_buyer
# -----------------------------------------
# CREATE BUYER ADDRESS
# -----------------------------------------

@router.post(
    "/{buyer_id}/addresses",
    response_model=BuyerAddressResponse,
    status_code=status.HTTP_201_CREATED
)
def create_buyer_address(
    buyer_id: int,
    address_data: BuyerAddressCreate,
    db: Session = Depends(get_db)
):
    try:
        address = buyer_address_service.create_address(
            db,
            buyer_id,
            address_data
        )

        return address

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error)
        )


# -----------------------------------------
# GET ALL BUYER ADDRESSES
# -----------------------------------------

@router.get(
    "/{buyer_id}/addresses",
    response_model=list[BuyerAddressResponse]
)
def get_buyer_addresses(
    buyer_id: int,
    db: Session = Depends(get_db)
):
    buyer = buyer_service.get_buyer_by_id(
        db,
        buyer_id
    )

    if not buyer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Buyer not found"
        )

    addresses = buyer_address_service.get_addresses_by_buyer_id(
        db,
        buyer_id
    )

    return addresses


# -----------------------------------------
# UPDATE BUYER ADDRESS
# -----------------------------------------

@router.patch(
    "/{buyer_id}/addresses/{address_id}",
    response_model=BuyerAddressResponse
)
def update_buyer_address(
    buyer_id: int,
    address_id: int,
    address_data: BuyerAddressUpdate,
    db: Session = Depends(get_db)
):
    # Check whether address exists
    address = buyer_address_service.get_address_by_id(
        db,
        address_id
    )

    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )

    # Ownership check
    if address.buyer_id != buyer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This address does not belong to the specified buyer"
        )

    updated_address = buyer_address_service.update_address(
        db,
        address,
        address_data
    )

    return updated_address


# -----------------------------------------
# DELETE BUYER ADDRESS
# -----------------------------------------

@router.delete(
    "/{buyer_id}/addresses/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_buyer_address(
    buyer_id: int,
    address_id: int,
    db: Session = Depends(get_db)
):
    # Check whether address exists
    address = buyer_address_service.get_address_by_id(
        db,
        address_id
    )

    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )

    # Ownership check
    if address.buyer_id != buyer_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This address does not belong to the specified buyer"
        )

    buyer_address_service.delete_address(
        db,
        address
    )

    return None