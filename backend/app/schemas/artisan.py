from pydantic import BaseModel, ConfigDict
from typing import Optional


# -----------------------------------------
# CREATE ARTISAN PROFILE
# -----------------------------------------

class ArtisanCreate(BaseModel):
    user_id: int

    location: str
    state: str
    district: str

    preferred_language: str
    craft_type: str

    profile_image: Optional[str] = None


# -----------------------------------------
# UPDATE ARTISAN PROFILE
# -----------------------------------------

class ArtisanUpdate(BaseModel):
    location: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None

    preferred_language: Optional[str] = None
    craft_type: Optional[str] = None

    profile_image: Optional[str] = None


# -----------------------------------------
# ARTISAN RESPONSE
# -----------------------------------------

class ArtisanResponse(BaseModel):
    id: int
    user_id: int

    location: str
    state: str
    district: str

    preferred_language: str
    craft_type: str

    profile_image: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True
    )