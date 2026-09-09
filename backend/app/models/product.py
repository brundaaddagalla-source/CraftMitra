from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Product(Base):
    __tablename__ = "products"

    # Primary identification
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    artisan_id: Mapped[int] = mapped_column(
        ForeignKey("artisan_profiles.id"),
        nullable=False,
        index=True
    )

    # Basic product information
    product_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    category: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    subcategory: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    # Craft information
    craft_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    craft_technique: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    material: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    color: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    pattern: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    # Dimensions
    length: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )

    width: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )

    dimension_unit: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    # Weight
    weight_value: Mapped[Decimal | None] = mapped_column(
        Numeric(10, 2),
        nullable=True
    )

    weight_unit: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    # Pricing
    base_price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    suggested_price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    final_price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="INR"
    )

    # Inventory
    stock_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    # Listing language
    original_language: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    # Voice / Audio AI integration
    voice_transcript: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    audio_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    # AI-generated content
    ai_generated_description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    ai_suggested_category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    ai_confidence: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 4),
        nullable=True
    )

    # Listing status
    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="draft"
    )

    visibility: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="public"
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

    # Relationships
    artisan = relationship(
        "ArtisanProfile",
        back_populates="products"
    )

    images = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    price_predictions = relationship(
        "PricePrediction",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    order_items = relationship(
        "OrderItem",
        back_populates="product"
    )