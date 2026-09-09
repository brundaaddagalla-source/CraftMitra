from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


# -----------------------------------------
# COMMON PRICE PREDICTION FIELDS
# -----------------------------------------

class PricePredictionBase(BaseModel):
    predicted_price: Decimal
    confidence: Decimal | None = None

    model_name: str | None = None
    model_version: str | None = None


# -----------------------------------------
# CREATE PRICE PREDICTION
# -----------------------------------------

class PricePredictionCreate(PricePredictionBase):
    product_id: int


# -----------------------------------------
# PRICE PREDICTION RESPONSE
# -----------------------------------------

class PricePredictionResponse(PricePredictionBase):
    id: int
    product_id: int
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )