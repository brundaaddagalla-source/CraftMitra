from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


# -----------------------------------------
# PASSWORD SECURITY
# -----------------------------------------

def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    hashed_password = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    return hashed_password.decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )


# -----------------------------------------
# JWT TOKEN SECURITY
# -----------------------------------------

def create_access_token(
    data: dict
) -> str:
    """
    Create a JWT access token.
    """

    token_data = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    token_data.update(
        {
            "exp": expire
        }
    )

    encoded_token = jwt.encode(
        token_data,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_token


def decode_access_token(
    token: str
) -> dict:
    """
    Decode and verify a JWT access token.

    Raises an exception if the token is invalid
    or expired.
    """

    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM]
    )

    return payload