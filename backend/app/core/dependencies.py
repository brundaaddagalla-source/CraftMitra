from fastapi import (
    Depends,
    HTTPException,
    status
)
from jwt import InvalidTokenError
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.models.user import User


security_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(
        security_scheme
    ),
    db: Session = Depends(get_db)
) -> User:
    """
    Extract and validate the JWT token and return
    the currently authenticated user.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:
        payload = decode_access_token(
            credentials.credentials
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        user = (
            db.query(User)
            .filter(User.id == int(user_id))
            .first()
        )

        if user is None:
            raise credentials_exception

        if not user.is_active:
            raise credentials_exception

        return user

    except (
        InvalidTokenError,
        ValueError,
        TypeError
    ):
        raise credentials_exception from None

    
def require_artisan(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Allow access only to users with the artisan role.
    """

    if current_user.role != "artisan":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Artisan access required"
        )

    return current_user


def require_buyer(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Allow access only to users with the buyer role.
    """

    if current_user.role != "buyer":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Buyer access required"
        )

    return current_user