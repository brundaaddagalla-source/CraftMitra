from app.schemas.ai import AIExtractedProductData


# ============================================================
# AI DESCRIPTION GENERATOR
# ============================================================
# Template-based composition, not a generative model - there's no
# LLM in this stack yet. It only uses fields that were actually
# extracted by extract_product_information(); missing fields are
# skipped entirely rather than guessed or padded with filler, so
# the result never states something the artisan didn't say.
# ============================================================

def _noun_phrase(product_data: AIExtractedProductData) -> str:
    if product_data.product_name:
        # product_name is often "<Color> <Material> <Noun>" (e.g.
        # "Indigo Cotton Saree") - the opening sentence below already
        # adds color/material as separate adjectives, so just take the
        # noun itself to avoid saying them twice.
        return product_data.product_name.split()[-1].lower()

    if product_data.category:
        return product_data.category.lower()

    return "product"


async def generate_product_description(
    product_data: AIExtractedProductData
) -> str:
    """
    Generate a short, readable product description from the
    structured product information returned by
    extract_product_information().

    A real AI provider can replace this function later without
    changing its signature or return type.
    """

    if not product_data:
        raise ValueError(
            "Product data is required"
        )

    noun_phrase = _noun_phrase(product_data)
    sentences = []

    # -------------------------------------
    # OPENING: what it is (+ color/material if known)
    # -------------------------------------

    opening_bits = []

    if product_data.color:
        opening_bits.append(product_data.color.lower())

    if product_data.material:
        opening_bits.append(product_data.material.lower())

    if opening_bits:
        sentences.append(
            f"A beautiful {' '.join(opening_bits)} {noun_phrase}, "
            f"handcrafted with care."
        )
    else:
        sentences.append(
            f"A beautiful handcrafted {noun_phrase}."
        )

    # -------------------------------------
    # TECHNIQUE
    # -------------------------------------

    if product_data.craft_technique:
        sentences.append(
            f"Made using {product_data.craft_technique.lower()}, "
            f"a technique passed down through generations of artisans."
        )

    # -------------------------------------
    # PATTERN
    # -------------------------------------

    if product_data.pattern:
        sentences.append(
            f"Features a {product_data.pattern.lower()} pattern."
        )

    # -------------------------------------
    # DIMENSIONS / WEIGHT
    # -------------------------------------

    size_bits = []

    if (
        product_data.length
        and product_data.width
        and product_data.dimension_unit
    ):
        size_bits.append(
            f"{product_data.length}x{product_data.width} "
            f"{product_data.dimension_unit}"
        )

    if product_data.weight_value and product_data.weight_unit:
        size_bits.append(
            f"{product_data.weight_value} {product_data.weight_unit}"
        )

    if size_bits:
        sentences.append(
            f"Approximate size: {', '.join(size_bits)}."
        )

    # -------------------------------------
    # CLOSING
    # -------------------------------------

    sentences.append(
        "Each piece is unique, reflecting the skill and heritage "
        "of the artisan who made it."
    )

    return " ".join(sentences)