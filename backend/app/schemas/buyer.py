from typing import Optional

from pydantic import BaseModel, ConfigDict


# -----------------------------------------
# CREATE BUYER PROFILE
# -----------------------------------------

class BuyerCreate(BaseModel):
    user_id: int

    location: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None


# -----------------------------------------
# UPDATE BUYER PROFILE
# -----------------------------------------

class BuyerUpdate(BaseModel):
    location: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None


# -----------------------------------------
# BUYER RESPONSE
# -----------------------------------------

class BuyerResponse(BaseModel):
    id: int
    user_id: int

    location: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True
    )