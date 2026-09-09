from typing import Optional

from pydantic import BaseModel, ConfigDict


# -----------------------------------------
# CREATE BUYER ADDRESS
# -----------------------------------------

class BuyerAddressCreate(BaseModel):
    address_line1: str
    address_line2: Optional[str] = None

    city: str
    district: Optional[str] = None
    state: str

    postal_code: str

    country: str = "India"

    is_default: bool = False


# -----------------------------------------
# UPDATE BUYER ADDRESS
# -----------------------------------------

class BuyerAddressUpdate(BaseModel):
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None

    city: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None

    postal_code: Optional[str] = None

    country: Optional[str] = None

    is_default: Optional[bool] = None


# -----------------------------------------
# BUYER ADDRESS RESPONSE
# -----------------------------------------

class BuyerAddressResponse(BaseModel):
    id: int
    buyer_id: int

    address_line1: str
    address_line2: Optional[str] = None

    city: str
    district: Optional[str] = None
    state: str

    postal_code: str
    country: str

    is_default: bool

    model_config = ConfigDict(
        from_attributes=True
    )