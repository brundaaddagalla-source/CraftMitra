import re


# ============================================================
# HIGH-CONFIDENCE ASR CORRECTIONS
# ============================================================
# Corrections are based on the actual ASR outputs observed
# during CraftMitra testing.
#
# Only clear ASR mistakes are corrected.
# Valid Telugu variants are preserved.
# ============================================================

WORD_CORRECTIONS = {

    # --------------------------------------------------------
    # Handmade / hand work
    # --------------------------------------------------------

    "చేత్తో": "చేతితో",

    # --------------------------------------------------------
    # Kondapalli
    # --------------------------------------------------------

    "కొణ్డపల్లి": "కొండపల్లి",

    # --------------------------------------------------------
    # Dolls
    # --------------------------------------------------------

    "బంబలు": "బొమ్మలు",

    # --------------------------------------------------------
    # Wood
    # --------------------------------------------------------

    "చక్కుతో": "చెక్కతో",
    "చక్కతో": "చెక్కతో",

    # --------------------------------------------------------
    # Verb
    # --------------------------------------------------------

    "చేస్నా": "చేశాను",

    # --------------------------------------------------------
    # Repeated-character ASR error
    # --------------------------------------------------------

    "చేేయడానికి": "చేయడానికి",
}


# ============================================================
# HIGH-CONFIDENCE PHRASE CORRECTIONS
# ============================================================
# Phrase corrections are used only when the intended phrase
# is clear from the ASR output.
# ============================================================

PHRASE_CORRECTIONS = {

    "చేత్తో చేసిన":
        "చేతితో చేసిన",

    "చేత్తో తయారు చేసిన":
        "చేతితో తయారు చేసిన",

    "చేత్తో తయారుచేసిన":
        "చేతితో తయారు చేసిన",

    "గీసి రంగులు వేసాను":
        "గీసి రంగులు వేశాను",
}


# ============================================================
# BASIC TELUGU CLEANUP
# ============================================================

def clean_telugu(text):
    """
    Basic cleanup of Telugu ASR output.

    Does not translate.
    Does not aggressively rewrite.
    """

    if not text:
        return ""

    text = text.strip()

    # Normalize repeated whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    # Remove spaces before punctuation
    text = re.sub(
        r"\s+([,.!?])",
        r"\1",
        text
    )

    # Add spaces after punctuation
    text = re.sub(
        r"([,.!?])([^\s])",
        r"\1 \2",
        text
    )

    return text.strip()


# ============================================================
# WORD-LEVEL ASR CORRECTIONS
# ============================================================

def apply_word_corrections(text):
    """
    Apply exact standalone-word corrections.

    This prevents a correction from accidentally changing
    part of another word.
    """

    if not text:
        return ""

    for wrong, correct in WORD_CORRECTIONS.items():

        pattern = (
            rf"(?<!\S)"
            rf"{re.escape(wrong)}"
            rf"(?!\S)"
        )

        text = re.sub(
            pattern,
            correct,
            text
        )

    return text


# ============================================================
# PHRASE-LEVEL CORRECTIONS
# ============================================================

def apply_phrase_corrections(text):
    """
    Apply high-confidence phrase-level corrections.
    """

    if not text:
        return ""

    for wrong, correct in PHRASE_CORRECTIONS.items():

        text = text.replace(
            wrong,
            correct
        )

    return text


# ============================================================
# REMOVE OBVIOUS REPETITIONS
# ============================================================

def remove_repeated_words(text):
    """
    Remove immediately repeated words.

    Example:
        "ఈ ఈ చీర"

    becomes:
        "ఈ చీర"

    Only consecutive repetitions are removed.
    """

    if not text:
        return ""

    words = text.split()

    if not words:
        return ""

    result = [words[0]]

    for word in words[1:]:

        if word == result[-1]:
            continue

        result.append(word)

    return " ".join(result)


# ============================================================
# SENTENCE BOUNDARY DETECTION
# ============================================================
# Based on sentence patterns observed in our actual
# handicraft / saree / wooden-artisan ASR outputs.
#
# These rules only add punctuation where the phrase itself
# forms a reasonably complete statement.
# ============================================================

SENTENCE_BOUNDARY_PHRASES = [

    # --------------------------------------------------------
    # Sarees / textiles
    # --------------------------------------------------------

    "ఈ చీరను నేను చేతితో తయారు చేశాను",

    "ఈ చీరను నేను నా చేతులతోనే తయారు చేశాను",

    "ఈ చీరను నేను నా సొంత చేతులతోనే చేశాను",

    "దీనికి కాటన్ వస్త్రాన్ని ఉపయోగించాను",

    "చీర మీద ఉన్న ప్రతి డిజైన్ చేతితో గీసి రంగులు వేశాను",

    "చీర మీద ఉన్న ప్రతి డిజైన్‌ను నా చేతులతోనే గీసి రంగులు వేశాను",

    "ఈ చీరకు సహజమైన రంగులు ఉపయోగించాను",

    "ఈ చీరపై సహజమైన రంగులు ఉపయోగించాను",

    "ఈ చీర మొత్తం తయారు చేయడానికి పది రోజులు పట్టింది",

    "ఈ చీర మొత్తం తయారు చేయడానికి దాదాపు రెండు వారాలు పడుతుంది",

    "వారం రోజులు పట్టింది చేయడానికి",

    # --------------------------------------------------------
    # Wooden handicrafts
    # --------------------------------------------------------

    "ఈ బొమ్మలను కొండపల్లిలో చేతితో తయారు చేస్తారు",

    "ఈ బొమ్మల కోసం తేలికపాటి చెక్కను ఉపయోగిస్తాము",

    "ముందుగా చెక్కను కావాల్సిన ఆకారంలో చెక్కుతాము",

    "చెక్కిన తర్వాత బొమ్మలకు సహజమైన రంగులతో రంగులు వేస్తాము",

    "ఒక్కో బొమ్మను తయారు చేయడానికి రెండు నుంచి మూడు రోజులు పడుతుంది",

    "ఈ బొమ్మలోని ప్రతి భాగాన్ని చేతితోనే తయారు చేశాను",

    # --------------------------------------------------------
    # General handicrafts
    # --------------------------------------------------------

    "మొదట ముడి పదార్థాలను సిద్ధం చేసి తర్వాత వాటికి ఆకారం ఇస్తాము",

    "చేతితో చేసే పని కాబట్టి ఒక్కో వస్తువును తయారు చేయడానికి ఎక్కువ సమయం పడుతుంది",

    "ఈ హస్తకళను తయారు చేయడంలో ఎక్కువ భాగం పని చేతితోనే చేస్తాము",
]


# ============================================================
# ADD SENTENCE BOUNDARIES
# ============================================================

def add_sentence_boundaries(text):
    """
    Add periods after known complete craft-related phrases.

    Does not perform general grammar-based sentence splitting.
    """

    if not text:
        return ""

    for phrase in SENTENCE_BOUNDARY_PHRASES:

        pattern = (
            rf"{re.escape(phrase)}"
            rf"(?![.!?])"
        )

        text = re.sub(
            pattern,
            phrase + ".",
            text
        )

    return text


# ============================================================
# PUNCTUATION CLEANUP
# ============================================================

def clean_punctuation(text):
    """
    Remove accidental repeated punctuation and whitespace.
    """

    if not text:
        return ""

    # Multiple periods → single period
    text = re.sub(
        r"\.{2,}",
        ".",
        text
    )

    # Multiple spaces
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    # Remove spaces before punctuation
    text = re.sub(
        r"\s+([,.!?])",
        r"\1",
        text
    )

    return text.strip()


# ============================================================
# FINAL PERIOD
# ============================================================

def add_final_period(text):
    """
    Add a final period to non-empty normalized text when
    punctuation is missing.
    """

    if not text:
        return ""

    text = text.strip()

    if text[-1] not in ".!?":
        text += "."

    return text


# ============================================================
# MAIN NORMALIZER
# ============================================================

def normalize_telugu(text):
    """
    CraftMitra Telugu ASR Normalizer.

    Pipeline:

        Raw ASR
           ↓
        Basic cleanup
           ↓
        ASR word corrections
           ↓
        Phrase corrections
           ↓
        Repetition removal
           ↓
        Sentence boundaries
           ↓
        Punctuation cleanup
           ↓
        Final punctuation
           ↓
        Normalized Telugu
    """

    if not text:
        return ""

    # 1. Basic cleanup
    text = clean_telugu(text)

    # 2. Correct confirmed ASR word errors
    text = apply_word_corrections(text)

    # 3. Correct confirmed ASR phrase errors
    text = apply_phrase_corrections(text)

    # 4. Remove obvious consecutive repetitions
    text = remove_repeated_words(text)

    # 5. Add known sentence boundaries
    text = add_sentence_boundaries(text)

    # 6. Final punctuation cleanup
    text = clean_punctuation(text)

    # 7. Ensure final punctuation
    text = add_final_period(text)

    return text