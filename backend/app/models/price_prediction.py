from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PricePrediction(Base):
    __tablename__ = "price_predictions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
        index=True
    )

    # ML predicted price
    predicted_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    # Confidence score of the prediction
    confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )

    # Model information
    model_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    model_version: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    # Prediction timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    product = relationship(
        "Product",
        back_populates="price_predictions"
    )