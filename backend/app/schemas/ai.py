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

    raw_transcript: str | None = None

    # Normalized transcript in the language the artisan actually spoke.
    regional_text: str | None = None

    # Deprecated alias of `regional_text`, only ever populated when
    # `processed_language` is "te". Kept so older frontend builds that
    # still read this field name don't break.
    normalized_telugu: str | None = None

    english: str | None = None

    hindi: str | None = None

    processed_language: str | None = None

    extracted_product: AIExtractedProductData | None = None

    ai_generated_description: str | None = None

    # Same AI-generated description, translated to Hindi - so the
    # review screen can show the description in regional / English /
    # Hindi without the artisan having to translate it themselves.
    ai_generated_description_hindi: str | None = None

    ai_suggested_category: str | None = None

    ai_confidence: float | None = Field(
        default=None,
        ge=0,
        le=1
    )