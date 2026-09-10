import re

from app.schemas.ai import AIExtractedProductData


# ============================================================
# HEURISTIC KNOWLEDGE BASE
# ============================================================
# There's no generative/LLM provider in this stack yet - only the
# speech-to-text and translation models are loaded. Until a real AI
# extraction provider is wired up, this is a deterministic
# keyword/regex extractor tuned for the kinds of Indian handicrafts
# CraftMitra artisans actually describe (sarees, wooden toys,
# pottery, jewellery...). It expects the ENGLISH translation of the
# artisan's voice description as input, not the raw spoken text.
#
# It's intentionally conservative: a field it isn't confident about
# is left as None rather than guessed, so the artisan can fill it in
# on the review screen instead of seeing something wrong.
# ============================================================

# (keyword, category, product noun) - the keyword that appears
# EARLIEST in the text wins, not the first one in this list, so
# "wooden toy" and "cotton saree" both resolve to the right noun
# regardless of which keyword happens to be listed first below.
PRODUCT_TYPE_KEYWORDS = [
    ("saree", "Handloom", "Saree"),
    ("sari", "Handloom", "Saree"),
    ("shawl", "Handloom", "Shawl"),
    ("scarf", "Handloom", "Scarf"),
    ("dupatta", "Handloom", "Dupatta"),
    ("doll", "Wood Craft", "Doll"),
    ("toy", "Wood Craft", "Toy"),
    ("carving", "Wood Craft", "Carving"),
    ("statue", "Wood Craft", "Statue"),
    ("pot", "Pottery", "Pot"),
    ("vase", "Pottery", "Vase"),
    ("necklace", "Jewellery", "Necklace"),
    ("bangle", "Jewellery", "Bangle"),
    ("earring", "Jewellery", "Earrings"),
    ("basket", "Handicraft", "Basket"),
]

MATERIAL_KEYWORDS = [
    "cotton", "silk", "wool", "jute", "bamboo", "wood", "clay",
    "terracotta", "brass", "silver", "gold", "copper", "leather",
    "cane", "wicker", "metal", "stone", "wax", "paper",
]

COLOR_KEYWORDS = [
    "indigo", "maroon", "turquoise", "beige", "golden", "cream",
    "red", "blue", "green", "yellow", "white", "black", "orange",
    "pink", "purple", "brown", "grey", "gray", "silver",
]

TECHNIQUE_KEYWORDS = [
    ("hand woven", "Traditional Hand Weaving"),
    ("hand-woven", "Traditional Hand Weaving"),
    ("woven by hand", "Traditional Hand Weaving"),
    ("handwoven", "Traditional Hand Weaving"),
    ("hand carved", "Hand Carving"),
    ("hand-carved", "Hand Carving"),
    ("carved by hand", "Hand Carving"),
    ("hand painted", "Hand Painting"),
    ("hand-painted", "Hand Painting"),
    ("painted by hand", "Hand Painting"),
    ("hand made", "Handmade"),
    ("handmade", "Handmade"),
    ("by hand", "Handmade"),
]

DIMENSION_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:x|by)\s*(\d+(?:\.\d+)?)\s*"
    r"(centimeters?|centimetres?|cm|inches?|inch|in|feet|foot|ft)",
    re.IGNORECASE,
)

WEIGHT_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(kilograms?|kilogram|kg|grams?|gram|g)\b",
    re.IGNORECASE,
)

DIMENSION_UNIT_MAP = {
    "cm": "cm", "centimeter": "cm", "centimeters": "cm",
    "centimetre": "cm", "centimetres": "cm",
    "in": "in", "inch": "in", "inches": "in",
    "ft": "ft", "foot": "ft", "feet": "ft",
}

WEIGHT_UNIT_MAP = {
    "kg": "kg", "kilogram": "kg", "kilograms": "kg",
    "g": "g", "gram": "g", "grams": "g",
}


def _first_keyword_match(text_lower, keywords):
    """Return whichever keyword appears earliest in the text, or None."""

    best_keyword = None
    best_index = None

    for keyword in keywords:
        index = text_lower.find(keyword)
        if index != -1 and (best_index is None or index < best_index):
            best_index = index
            best_keyword = keyword

    return best_keyword


def _first_tuple_match(text_lower, pairs):
    """Same as _first_keyword_match, but for (keyword, value) pairs."""

    best_value = None
    best_index = None

    for keyword, value in pairs:
        index = text_lower.find(keyword)
        if index != -1 and (best_index is None or index < best_index):
            best_index = index
            best_value = value

    return best_value


# ============================================================
# PRODUCT AI EXTRACTOR
# ============================================================

async def extract_product_information(
    text: str,
    language: str | None = None
) -> AIExtractedProductData:
    """
    Extract structured product information from natural-language
    product text (expects the English translation of the artisan's
    voice description - see ai_product_pipeline_service.py).

    This is a deterministic keyword/regex extractor, not a trained
    model. A real AI provider can replace this function later
    without changing its signature or return type.
    """

    if not text or not text.strip():
        raise ValueError(
            "Product text cannot be empty"
        )

    text_lower = text.lower()

    # -------------------------------------
    # PRODUCT TYPE / CATEGORY
    # -------------------------------------

    category = None
    product_noun = None
    best_index = None

    for keyword, keyword_category, noun in PRODUCT_TYPE_KEYWORDS:
        index = text_lower.find(keyword)
        if index != -1 and (best_index is None or index < best_index):
            best_index = index
            category = keyword_category
            product_noun = noun

    # -------------------------------------
    # MATERIAL / COLOR / TECHNIQUE
    # -------------------------------------

    material = _first_keyword_match(text_lower, MATERIAL_KEYWORDS)
    color = _first_keyword_match(text_lower, COLOR_KEYWORDS)
    craft_technique = _first_tuple_match(text_lower, TECHNIQUE_KEYWORDS)

    # -------------------------------------
    # DIMENSIONS / WEIGHT
    # -------------------------------------

    length = width = dimension_unit = None
    dimension_match = DIMENSION_PATTERN.search(text_lower)

    if dimension_match:
        length = float(dimension_match.group(1))
        width = float(dimension_match.group(2))
        dimension_unit = DIMENSION_UNIT_MAP.get(
            dimension_match.group(3).lower()
        )

    weight_value = weight_unit = None
    weight_match = WEIGHT_PATTERN.search(text_lower)

    if weight_match:
        weight_value = float(weight_match.group(1))
        weight_unit = WEIGHT_UNIT_MAP.get(
            weight_match.group(2).lower()
        )

    # -------------------------------------
    # PRODUCT NAME
    # -------------------------------------

    name_parts = [
        part for part in (color, material, product_noun) if part
    ]

    product_name = (
        " ".join(name_parts).title()
        if name_parts
        else None
    )

    return AIExtractedProductData(
        product_name=product_name,
        category=category,
        subcategory=None,
        description=text.strip(),
        craft_type=category,
        craft_technique=craft_technique,
        material=material.title() if material else None,
        color=color.title() if color else None,
        pattern=None,
        length=length,
        width=width,
        dimension_unit=dimension_unit,
        weight_value=weight_value,
        weight_unit=weight_unit,
    )