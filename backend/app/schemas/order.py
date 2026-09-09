from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.order_item import (
    OrderItemCreate,
    OrderItemResponse
)


# -----------------------------------------
# DELIVERY ADDRESS SNAPSHOT
# -----------------------------------------

class DeliveryAddress(BaseModel):
    address_line1: str
    address_line2: str | None = None

    city: str
    district: str | None = None

    state: str
    postal_code: str

    country: str = "India"


# -----------------------------------------
# COMMON ORDER FIELDS
# -----------------------------------------

class OrderBase(BaseModel):
    currency: str = "INR"


# -----------------------------------------
# CREATE ORDER
# -----------------------------------------

class OrderCreate(OrderBase):
    buyer_id: int

    delivery_address: DeliveryAddress | None = None

    items: list[OrderItemCreate] = Field(
        min_length=1
    )


# -----------------------------------------
# UPDATE ORDER
# -----------------------------------------

class OrderUpdate(BaseModel):
    status: str | None = None
    payment_status: str | None = None


# -----------------------------------------
# ORDER RESPONSE
# -----------------------------------------

class OrderResponse(OrderBase):
    id: int
    buyer_id: int

    total_amount: Decimal

    status: str
    payment_status: str

    delivery_address: dict | None

    created_at: datetime
    updated_at: datetime

    items: list[OrderItemResponse] = Field(
        default_factory=list
    )

    model_config = ConfigDict(
        from_attributes=True
    )