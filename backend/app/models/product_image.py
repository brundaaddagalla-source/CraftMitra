from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ProductImage(Base):
    __tablename__ = "product_images"

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

    # =========================================
    # ORIGINAL IMAGE
    # =========================================

    image_url: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    # =========================================
    # AI ENHANCED IMAGE
    # =========================================

    enhanced_image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    # pending / processing / completed / failed
    processing_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending"
    )

    # =========================================
    # IMAGE SETTINGS
    # =========================================

    is_primary: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    # =========================================
    # RELATIONSHIP
    # =========================================

    product = relationship(
        "Product",
        back_populates="images"
    )