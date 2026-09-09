from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    verify_password
)
from app.models.user import User
from app.schemas.auth import LoginRequest
from app.services.user_service import get_user_by_email


def authenticate_user(
    db: Session,
    login_data: LoginRequest
) -> str | None:
    """
    Authenticate a user using email and password.

    Returns a JWT access token if authentication
    is successful. Otherwise returns None.
    """

    # Find user by email
    user = get_user_by_email(
        db,
        login_data.email
    )

    # User does not exist
    if not user:
        return None

    # Account is inactive
    if not user.is_active:
        return None

    # Verify password
    password_valid = verify_password(
        login_data.password,
        user.password_hash
    )

    if not password_valid:
        return None

    # Create JWT token
    access_token = create_access_token(
        {
            "sub": str(user.id)
        }
    )

    return access_token