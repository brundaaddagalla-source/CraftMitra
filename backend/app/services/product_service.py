from sqlalchemy.orm import Session

from app.models.artisan_profile import ArtisanProfile
from app.models.product import Product

from app.schemas.product import (
    ProductCreate,
    ProductUpdate
)


# =========================================
# HELPER: GET PRODUCT BY ID
# =========================================

def get_product_by_id(
    db: Session,
    product_id: int
):
    return (
        db.query(Product)
        .filter(Product.id == product_id)
        .first()
    )


# =========================================
# HELPER: GET PRODUCTS BY ARTISAN
# =========================================

def get_products_by_artisan_id(
    db: Session,
    artisan_id: int
):
    return (
        db.query(Product)
        .filter(Product.artisan_id == artisan_id)
        .all()
    )


# =========================================
# HELPER: CHECK ARTISAN EXISTS
# =========================================

def get_artisan_by_id(
    db: Session,
    artisan_id: int
):
    return (
        db.query(ArtisanProfile)
        .filter(ArtisanProfile.id == artisan_id)
        .first()
    )


# =========================================
# HELPER: CONVERT PRODUCT TO API RESPONSE
# =========================================

def product_to_response(product: Product):
    """
    Convert the flat SQLAlchemy Product model
    into the nested frontend API structure.
    """

    return {
        "id": product.id,
        "artisan_id": product.artisan_id,

        "product_name": product.product_name,
        "category": product.category,
        "subcategory": product.subcategory,
        "description": product.description,

        "craft_details": {
            "craft_type": product.craft_type,
            "craft_technique": product.craft_technique,
            "material": product.material,
            "color": product.color,
            "pattern": product.pattern,

            "dimensions": {
                "length": product.length,
                "width": product.width,
                "unit": product.dimension_unit
            },

            "weight": {
                "value": product.weight_value,
                "unit": product.weight_unit
            }
        },

        "pricing": {
            "base_price": product.base_price,
            "suggested_price": product.suggested_price,
            "final_price": product.final_price,
            "currency": product.currency
        },

        "inventory": {
            "stock_quantity": product.stock_quantity
        },

        "original_language": product.original_language,

        "voice_input": {
            "transcript": product.voice_transcript,
            "audio_url": product.audio_url
        },

        "ai": {
            "generated_description": product.ai_generated_description,
            "suggested_category": product.ai_suggested_category,
            "confidence": product.ai_confidence
        },

        "status": product.status,
        "visibility": product.visibility
    }


# =========================================
# CREATE PRODUCT
# =========================================

def create_product(
    db: Session,
    product_data: ProductCreate
):
    # -------------------------------------
    # CHECK ARTISAN EXISTS
    # -------------------------------------

    artisan = get_artisan_by_id(
        db,
        product_data.artisan_id
    )

    if not artisan:
        raise ValueError(
            "Artisan not found"
        )

    # -------------------------------------
    # EXTRACT OPTIONAL NESTED DATA
    # -------------------------------------

    craft = product_data.craft_details

    pricing = product_data.pricing
    inventory = product_data.inventory
    voice_input = product_data.voice_input
    ai = product_data.ai

    # -------------------------------------
    # CREATE PRODUCT
    # -------------------------------------

    new_product = Product(
        artisan_id=product_data.artisan_id,

        # Basic information
        product_name=product_data.product_name,
        category=product_data.category,
        subcategory=product_data.subcategory,
        description=product_data.description,

        # Craft information
        craft_type=craft.craft_type or product_data.category,
        craft_technique=craft.craft_technique,
        material=craft.material,
        color=craft.color,
        pattern=craft.pattern,

        # Dimensions
        length=(
            craft.dimensions.length
            if craft.dimensions
            else None
        ),

        width=(
            craft.dimensions.width
            if craft.dimensions
            else None
        ),

        dimension_unit=(
            craft.dimensions.unit
            if craft.dimensions
            else None
        ),

        # Weight
        weight_value=(
            craft.weight.value
            if craft.weight
            else None
        ),

        weight_unit=(
            craft.weight.unit
            if craft.weight
            else None
        ),

        # Pricing
        base_price=(
            pricing.base_price
            if pricing
            else None
        ),

        suggested_price=(
            pricing.suggested_price
            if pricing
            else None
        ),

        final_price=(
            pricing.final_price
            if pricing
            else None
        ),

        currency=(
            pricing.currency
            if pricing and pricing.currency
            else "INR"
        ),

        # Inventory
        stock_quantity=(
            inventory.stock_quantity
            if inventory
            else 0
        ),

        # Language
        original_language=product_data.original_language,

        # Voice input
        voice_transcript=(
            voice_input.transcript
            if voice_input
            else None
        ),

        audio_url=(
            voice_input.audio_url
            if voice_input
            else None
        ),

        # AI information
        ai_generated_description=(
            ai.generated_description
            if ai
            else None
        ),

        ai_suggested_category=(
            ai.suggested_category
            if ai
            else None
        ),

        ai_confidence=(
            ai.confidence
            if ai
            else None
        ),

        # Listing
        status=product_data.status or "draft",
        visibility=product_data.visibility or "public"
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    return new_product


# =========================================
# UPDATE PRODUCT
# =========================================

def update_product(
    db: Session,
    product: Product,
    product_data: ProductUpdate
):
    """
    Update only fields supplied by the frontend.
    """

    update_data = product_data.model_dump(
        exclude_unset=True
    )

    # -------------------------------------
    # BASIC FIELDS
    # -------------------------------------

    basic_fields = [
        "product_name",
        "category",
        "subcategory",
        "description",
        "original_language",
        "status",
        "visibility"
    ]

    for field in basic_fields:
        if field in update_data:
            setattr(
                product,
                field,
                update_data[field]
            )

    # -------------------------------------
    # CRAFT DETAILS
    # -------------------------------------

    if "craft_details" in update_data:
        craft = update_data["craft_details"]

        if "craft_type" in craft:
            product.craft_type = craft["craft_type"]

        if "craft_technique" in craft:
            product.craft_technique = craft["craft_technique"]

        if "material" in craft:
            product.material = craft["material"]

        if "color" in craft:
            product.color = craft["color"]

        if "pattern" in craft:
            product.pattern = craft["pattern"]

        # Dimensions
        if "dimensions" in craft:
            dimensions = craft["dimensions"]

            if dimensions is not None:
                if "length" in dimensions:
                    product.length = dimensions["length"]

                if "width" in dimensions:
                    product.width = dimensions["width"]

                if "unit" in dimensions:
                    product.dimension_unit = dimensions["unit"]

        # Weight
        if "weight" in craft:
            weight = craft["weight"]

            if weight is not None:
                if "value" in weight:
                    product.weight_value = weight["value"]

                if "unit" in weight:
                    product.weight_unit = weight["unit"]

    # -------------------------------------
    # PRICING
    # -------------------------------------

    if "pricing" in update_data:
        pricing = update_data["pricing"]

        if pricing is not None:
            if "base_price" in pricing:
                product.base_price = pricing["base_price"]

            if "suggested_price" in pricing:
                product.suggested_price = pricing["suggested_price"]

            if "final_price" in pricing:
                product.final_price = pricing["final_price"]

            if "currency" in pricing:
                product.currency = pricing["currency"]

    # -------------------------------------
    # INVENTORY
    # -------------------------------------

    if "inventory" in update_data:
        inventory = update_data["inventory"]

        if inventory is not None:
            if "stock_quantity" in inventory:
                product.stock_quantity = inventory["stock_quantity"]

    # -------------------------------------
    # VOICE INPUT
    # -------------------------------------

    if "voice_input" in update_data:
        voice_input = update_data["voice_input"]

        if voice_input is not None:
            if "transcript" in voice_input:
                product.voice_transcript = voice_input[
                    "transcript"
                ]

            if "audio_url" in voice_input:
                product.audio_url = voice_input[
                    "audio_url"
                ]

    # -------------------------------------
    # AI INFORMATION
    # -------------------------------------

    if "ai" in update_data:
        ai = update_data["ai"]

        if ai is not None:
            if "generated_description" in ai:
                product.ai_generated_description = ai[
                    "generated_description"
                ]

            if "suggested_category" in ai:
                product.ai_suggested_category = ai[
                    "suggested_category"
                ]

            if "confidence" in ai:
                product.ai_confidence = ai[
                    "confidence"
                ]

    db.commit()
    db.refresh(product)

    return product


# =========================================
# DELETE PRODUCT
# =========================================

def delete_product(
    db: Session,
    product: Product
):
    db.delete(product)
    db.commit()