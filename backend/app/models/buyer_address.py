from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class BuyerAddress(Base):
    __tablename__ = "buyer_addresses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    buyer_id: Mapped[int] = mapped_column(
        ForeignKey("buyer_profiles.id"),
        nullable=False,
        index=True
    )

    address_line1: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    address_line2: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    city: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    district: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    state: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    postal_code: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    country: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="India"
    )

    is_default: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    buyer = relationship(
        "BuyerProfile",
        back_populates="addresses"
    )