from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ArtisanProfile(Base):
    __tablename__ = "artisan_profiles"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    location: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    state: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    district: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    preferred_language: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    craft_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    profile_image: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="artisan_profile"
    )
    products = relationship(
        "Product",
        back_populates="artisan"
    )