from pydantic import BaseModel, Field


# =========================================
# AI PRODUCT INPUT
# =========================================

class AIProductInput(BaseModel):

    transcript: str = Field(
        ...,
        min_length=1,
        description="Transcript obtained from artisan audio"
    )

    original_language: str | None = Field(
        default=None,
        description="Language of the original transcript"
    )


# =========================================
# AI EXTRACTED PRODUCT DATA
# =========================================

class AIExtractedProductData(BaseModel):

    product_name: str | None = None

    category: str | None = None

    subcategory: str | None = None

    description: str | None = None

    craft_type: str | None = None

    craft_technique: str | None = None

    material: str | None = None

    color: str | None = None

    pattern: str | None = None

    length: float | None = None

    width: float | None = None

    dimension_unit: str | None = None

    weight_value: float | None = None

    weight_unit: str | None = None


# =========================================
# TRANSCRIPTION RESPONSE
# =========================================

class TranscriptionResponse(BaseModel):

    transcript: str

    detected_language: str | None = None


# =========================================
# AI PRODUCT PROCESSING RESPONSE
# =========================================

class AIProductProcessingResponse(BaseModel):

    transcript: str

    processed_language: str | None = None

    extracted_product: AIExtractedProductData

    ai_generated_description: str | None = None

    ai_suggested_category: str | None = None

    ai_confidence: float | None = Field(
        default=None,
        ge=0,
        le=1
    )