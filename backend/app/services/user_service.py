from sqlalchemy.orm import Session
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


def get_user_by_id(
    db: Session,
    user_id: int
):
    return (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


def get_user_by_email(
    db: Session,
    email: str
):
    return (
        db.query(User)
        .filter(User.email == email)
        .first()
    )


def get_user_by_phone(
    db: Session,
    phone: str
):
    return (
        db.query(User)
        .filter(User.phone == phone)
        .first()
    )


def create_user(
    db: Session,
    user_data: UserCreate
):
    # Check duplicate email
    existing_email = get_user_by_email(
        db,
        user_data.email
    )

    if existing_email:
        raise ValueError(
            "Email is already registered"
        )

    # Check duplicate phone
    existing_phone = get_user_by_phone(
        db,
        user_data.phone
    )

    if existing_phone:
        raise ValueError(
            "Phone number is already registered"
        )

# Hash password before storing it
    hashed_password = hash_password(
        user_data.password
    )


    new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=hashed_password,
        role=user_data.role
    )

    db.add(new_user)

    db.commit()

    db.refresh(new_user)

    return new_user


def update_user(
    db: Session,
    user: User,
    user_data: UserUpdate
):
    update_data = user_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            user,
            field,
            value
        )

    db.commit()

    db.refresh(user)

    return user