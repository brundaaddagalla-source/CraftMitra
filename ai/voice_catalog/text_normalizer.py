
DOMAIN_CORRECTIONS = {

    # --------------------------------------------------------
    # Sarees / textiles
    # --------------------------------------------------------

    "నీ చీర మీద": "ఈ చీర మీద",

    # Common phrase variations
    "చీర మీద ఉన్న": "చీర మీద ఉన్న",
    "చీరపై ఉన్న": "చీరపై ఉన్న",

    # --------------------------------------------------------
    # Handmade / hand work
    # --------------------------------------------------------

    "చేత్తో చేసిన": "చేతితో చేసిన",
    "చేత్తో తయారు చేసిన": "చేతితో తయారు చేసిన",

    # --------------------------------------------------------
    # Painting / drawing
    # --------------------------------------------------------

    "గీసి రంగులు వేశాను": "గీసి రంగులు వేశాను",

    # --------------------------------------------------------
    # Wood carving
    # --------------------------------------------------------

    "చెక్కతో చెక్కుతారు": "చెక్కతో చెక్కుతారు",
    "చెక్కతో చెక్కిన": "చెక్కతో చెక్కిన",

    # --------------------------------------------------------
    # Kondapalli
    # --------------------------------------------------------

    # Preserve the phrase as a known handicraft term.
    "కొండపల్లి బొమ్మలు": "కొండపల్లి బొమ్మలు",
    "కొండపల్లి బొమ్మ": "కొండపల్లి బొమ్మ",
}


# ============================================================
# GENERAL TELUGU CLEANUP
# ============================================================

def clean_telugu(text):
    """
    Basic cleanup of Telugu ASR output.

    Does NOT translate.
    Does NOT aggressively rewrite sentences.
    """

    if not text:
        return ""

    text = text.strip()

    # Remove repeated whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove spaces before punctuation
    text = re.sub(r"\s+([,.!?])", r"\1", text)

    # Add a space after punctuation if another character follows
    text = re.sub(r"([,.!?])([^\s])", r"\1 \2", text)

    return text.strip()


# ============================================================
# DOMAIN-AWARE CORRECTION
# ============================================================

def apply_domain_corrections(text):
    """
    Apply only high-confidence phrase-level corrections.

    Phrase-level replacement is safer than replacing individual
    words because individual Telugu words can have multiple meanings.
    """

    for wrong, correct in DOMAIN_CORRECTIONS.items():

        text = text.replace(
            wrong,
            correct
        )

    return text


# ============================================================
# SENTENCE SEGMENTATION
# ============================================================

def add_sentence_boundaries(text):
    """
    Adds basic sentence boundaries to long ASR output.

    This is intentionally conservative.

    We mainly use common Telugu sentence-ending patterns.
    """

    if not text:
        return ""

    # Common transition phrases in artisan descriptions.

    replacements = {

        "వారం రోజులు పట్టింది చేయడానికి":
            "వారం రోజులు పట్టింది చేయడానికి.",

        "వీటిని చెక్కతో చెక్కుతారు":
            "వీటిని చెక్కతో చెక్కుతారు.",

    }

    for phrase, replacement in replacements.items():

        text = text.replace(
            phrase,
            replacement
        )

    return text


# ============================================================
# MAIN NORMALIZER
# ============================================================

def normalize_telugu(text):
    """
    Main Telugu normalization pipeline.

    Flow:

        Raw ASR
           ↓
        Basic cleanup
           ↓
        High-confidence domain corrections
           ↓
        Sentence boundaries
           ↓
        Normalized Telugu
    """

    if not text:
        return ""

    # Step 1
    text = clean_telugu(text)

    # Step 2
    text = apply_domain_corrections(text)

    # Step 3
    text = add_sentence_boundaries(text)

    # Final cleanup
    text = clean_telugu(text)

    return text


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_sentences = [

        "ఈ చీరను నేను నా సొంత చేతులతోనే చేశాను "
        "వారం రోజులు పట్టింది చేయడానికి "
        "నీ చీర మీద ఉన్న ప్రతి బొమ్మ "
        "నేను నా చేతులతో గీసి రంగులు వేశాను",

        "ఇవి చేత్తో చేసిన కొండపల్లి బొమ్మలు "
        "వీటిని చెక్కతో చెక్కుతారు",
    ]

    print("=" * 60)
    print("TELUGU NORMALIZER TEST")
    print("=" * 60)

    for i, text in enumerate(test_sentences, 1):

        print(f"\nTEST {i}")
        print("-" * 60)

        print("RAW:")
        print(text)

        normalized = normalize_telugu(text)

        print("\nNORMALIZED:")
        print(normalized)