from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict


# =========================================
# NESTED PRODUCT SCHEMAS
# =========================================


# -----------------------------------------
# DIMENSIONS
# -----------------------------------------

class ProductDimensions(BaseModel):
    length: Optional[Decimal] = None
    width: Optional[Decimal] = None
    unit: Optional[str] = None


# -----------------------------------------
# WEIGHT
# -----------------------------------------

class ProductWeight(BaseModel):
    value: Optional[Decimal] = None
    unit: Optional[str] = None


# -----------------------------------------
# CRAFT DETAILS
# -----------------------------------------

class CraftDetails(BaseModel):
    craft_type: Optional[str] = None
    craft_technique: Optional[str] = None
    material: Optional[str] = None
    color: Optional[str] = None
    pattern: Optional[str] = None

    dimensions: Optional[ProductDimensions] = None
    weight: Optional[ProductWeight] = None


# -----------------------------------------
# PRICING
# -----------------------------------------

class ProductPricing(BaseModel):
    base_price: Optional[Decimal] = None
    suggested_price: Optional[Decimal] = None
    final_price: Optional[Decimal] = None

    currency: Optional[str] = "INR"


# -----------------------------------------
# INVENTORY
# -----------------------------------------

class ProductInventory(BaseModel):
    stock_quantity: Optional[int] = 0


# -----------------------------------------
# VOICE INPUT
# -----------------------------------------

class VoiceInput(BaseModel):
    transcript: Optional[str] = None
    audio_url: Optional[str] = None


# -----------------------------------------
# AI INFORMATION
# -----------------------------------------

class ProductAI(BaseModel):
    generated_description: Optional[str] = None
    suggested_category: Optional[str] = None
    confidence: Optional[Decimal] = None


# =========================================
# PRODUCT CREATE
# =========================================

class ProductCreate(BaseModel):

    # Artisan relationship
    artisan_id: int

    # Basic information
    product_name: str
    category: str

    subcategory: Optional[str] = None
    description: Optional[str] = None

    # Craft information
    craft_details: CraftDetails

    # Pricing
    pricing: Optional[ProductPricing] = None

    # Inventory
    inventory: Optional[ProductInventory] = None

    # Language
    original_language: Optional[str] = None

    # Voice input
    voice_input: Optional[VoiceInput] = None

    # AI generated information
    ai: Optional[ProductAI] = None

    # Listing
    status: Optional[str] = "draft"
    visibility: Optional[str] = "public"


# =========================================
# PRODUCT UPDATE
# =========================================

class ProductUpdate(BaseModel):

    product_name: Optional[str] = None
    category: Optional[str] = None

    subcategory: Optional[str] = None
    description: Optional[str] = None

    craft_details: Optional[CraftDetails] = None

    pricing: Optional[ProductPricing] = None

    inventory: Optional[ProductInventory] = None

    original_language: Optional[str] = None

    voice_input: Optional[VoiceInput] = None

    ai: Optional[ProductAI] = None

    status: Optional[str] = None
    visibility: Optional[str] = None


# =========================================
# PRODUCT RESPONSE
# =========================================

class ProductResponse(BaseModel):

    id: int
    artisan_id: int

    # Basic information
    product_name: str
    category: str

    subcategory: Optional[str] = None
    description: Optional[str] = None

    # Craft details
    craft_details: CraftDetails

    # Pricing
    pricing: ProductPricing

    # Inventory
    inventory: ProductInventory

    # Language
    original_language: Optional[str] = None

    # Voice input
    voice_input: VoiceInput

    # AI information
    ai: ProductAI

    # Listing
    status: str
    visibility: str

    model_config = ConfigDict(
        from_attributes=True
    )