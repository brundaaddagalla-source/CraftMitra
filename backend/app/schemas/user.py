from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# -----------------------------------------
# COMMON USER FIELDS
# -----------------------------------------

class UserBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=150
    )

    email: EmailStr

    phone: str = Field(
        min_length=5,
        max_length=20
    )

    role: str = "artisan"


# -----------------------------------------
# USER REGISTRATION
# -----------------------------------------

class UserCreate(UserBase):
    password: str = Field(
        min_length=6,
        max_length=100
    )


# -----------------------------------------
# USER UPDATE
# -----------------------------------------

class UserUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    phone: str | None = Field(
        default=None,
        min_length=5,
        max_length=20
    )

    role: str | None = None

    is_active: bool | None = None


# -----------------------------------------
# USER RESPONSE
# -----------------------------------------

class UserResponse(UserBase):
    id: int

    is_active: bool

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )