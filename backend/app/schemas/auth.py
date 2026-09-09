from pydantic import BaseModel, EmailStr, Field


# -----------------------------------------
# LOGIN REQUEST
# -----------------------------------------

class LoginRequest(BaseModel):
    email: EmailStr

    password: str = Field(
        min_length=6,
        max_length=100
    )


# -----------------------------------------
# LOGIN RESPONSE
# -----------------------------------------

class TokenResponse(BaseModel):
    access_token: str

    token_type: str = "bearer"