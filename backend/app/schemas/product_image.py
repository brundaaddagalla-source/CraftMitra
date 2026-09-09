from datetime import datetime

from pydantic import BaseModel, ConfigDict


# =========================================
# CREATE PRODUCT IMAGE
# =========================================

class ProductImageCreate(BaseModel):

    # Original image URL
    image_url: str

    is_primary: bool = False


# =========================================
# UPDATE PRODUCT IMAGE
# =========================================

class ProductImageUpdate(BaseModel):

    # Update original image URL
    image_url: str | None = None

    # Change primary image
    is_primary: bool | None = None

# =========================================
# AI ENHANCEMENT RESULT
# =========================================

class ProductImageEnhancementResult(BaseModel):

    enhanced_image_url: str


# =========================================
# PRODUCT IMAGE RESPONSE
# =========================================

class ProductImageResponse(BaseModel):

    id: int

    product_id: int

    # Original image
    image_url: str

    # AI enhanced image
    enhanced_image_url: str | None = None

    # pending / processing / completed / failed
    processing_status: str

    # Product image settings
    is_primary: bool

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )