from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


# -----------------------------------------
# COMMON ORDER ITEM FIELDS
# -----------------------------------------

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = 1
    unit_price: Decimal


# -----------------------------------------
# CREATE ORDER ITEM
# -----------------------------------------

class OrderItemCreate(OrderItemBase):
    pass


# -----------------------------------------
# ORDER ITEM RESPONSE
# -----------------------------------------

class OrderItemResponse(OrderItemBase):
    id: int
    order_id: int
    subtotal: Decimal
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )