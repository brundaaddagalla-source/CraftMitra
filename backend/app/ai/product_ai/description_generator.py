from app.schemas.ai import AIExtractedProductData


# =========================================
# AI DESCRIPTION GENERATOR FOUNDATION
# =========================================

async def generate_product_description(
    product_data: AIExtractedProductData
) -> str:
    """
    Generate a professional product description
    from structured product information.

    The AI model will eventually use product
    attributes such as:

    - Product name
    - Category
    - Craft type
    - Craft technique
    - Material
    - Color
    - Pattern
    - Dimensions
    - Weight

    to generate a clear and attractive
    product description.

    This is currently a provider-independent
    foundation.

    A real AI model/provider will be
    integrated later.
    """

    # -------------------------------------
    # BASIC VALIDATION
    # -------------------------------------

    if not product_data:
        raise ValueError(
            "Product data is required"
        )

    # -------------------------------------
    # FUTURE AI DESCRIPTION GENERATION
    # -------------------------------------

    raise NotImplementedError(
        "No AI description generation provider has been configured yet"
    )