from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class BuyerProfile(Base):
    __tablename__ = "buyer_profiles"

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

    location: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True
    )

    state: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    district: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="buyer_profile"
    )

    orders = relationship(
        "Order",
        back_populates="buyer"
    )

    addresses = relationship(
        "BuyerAddress",
        back_populates="buyer",
        cascade="all, delete-orphan"
    )