from app.schemas.ai import AIExtractedProductData


# =========================================
# PRODUCT AI EXTRACTOR FOUNDATION
# =========================================

async def extract_product_information(
    text: str,
    language: str | None = None
) -> AIExtractedProductData:
    """
    Extract structured product information
    from natural-language product text.

    The AI model will eventually analyze the
    artisan's transcript and extract product
    attributes such as:

    - Product name
    - Category
    - Subcategory
    - Craft type
    - Craft technique
    - Material
    - Color
    - Pattern
    - Dimensions
    - Weight

    This is currently a provider-independent
    foundation.

    A real AI model/provider will be
    integrated later.
    """

    # -------------------------------------
    # VALIDATE INPUT
    # -------------------------------------

    if not text or not text.strip():
        raise ValueError(
            "Product text cannot be empty"
        )

    # -------------------------------------
    # FUTURE AI EXTRACTION
    # -------------------------------------

    raise NotImplementedError(
        "No AI product extraction provider has been configured yet"
    )