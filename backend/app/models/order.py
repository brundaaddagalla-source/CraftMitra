from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Order(Base):
    __tablename__ = "orders"

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

    # Total amount for the order
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="INR"
    )

    # Order lifecycle
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending"
    )

    # Payment information
    payment_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending"
    )

        # Snapshot of delivery address at the time of ordering
    delivery_address: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    buyer = relationship(
        "BuyerProfile",
        back_populates="orders"
    )

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )