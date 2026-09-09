import re
import unicodedata


# ============================================================
# 1. KNOWN STT CORRECTIONS
# ============================================================
#
# These are recurring errors observed from the Swecha ASR.
#
# IMPORTANT:
# This dictionary should contain ASR-specific mistakes,
# NOT the entire Telugu vocabulary.
#
# We will expand this based on real ASR outputs.
# ============================================================

TELUGU_CORRECTIONS = {

    # Handicrafts / current demo
    "చేత్తో": "చేతితో",
    "చేస్నా": "చేసిన",
    "కొణ్డపల్లి": "కొండపల్లి",
    "బంబలు": "బొమ్మలు",
    "బొంబలు": "బొమ్మలు",
    "బొంబలో": "బొమ్మలు",
    "విటిన": "వీటిని",
    "చక్కుతో": "చెక్కుతో",
    "చక్కతో": "చెక్కుతో",
    "చిక్కుతారు": "చెక్కుతారు",

    # Agriculture / general examples
    "పనీ": "పని",
    "చేస్థున్నారు": "చేస్తున్నారు",
    "చేస్టున్నారు": "చేస్తున్నారు",
    "చేస్తునారు": "చేస్తున్నారు",

    # Common spelling errors
    "వెల్తున్నాడు": "వెళ్తున్నాడు",
    "వెల్తుంది": "వెళ్తుంది",
    "వెల్తున్నారు": "వెళ్తున్నారు",
    "బాష": "భాష",
    "చాల": "చాలా",
}


# ============================================================
# 2. UNICODE NORMALIZATION
# ============================================================

def normalize_unicode(text):
    """
    Convert equivalent Unicode representations into
    standard NFC form.
    """

    return unicodedata.normalize("NFC", text)


# ============================================================
# 3. BASIC TEXT CLEANING
# ============================================================

def clean_text(text):
    """
    General text cleanup.

    Works for arbitrary Telugu text.
    """

    # Remove leading/trailing whitespace
    text = text.strip()

    # Replace multiple spaces/newlines/tabs with one space
    text = re.sub(r"\s+", " ", text)

    # Remove spaces before punctuation
    text = re.sub(
        r"\s+([,.!?;:])",
        r"\1",
        text
    )

    # Add space after punctuation when missing
    text = re.sub(
        r"([,.!?;:])(?=\S)",
        r"\1 ",
        text
    )

    # Remove repeated punctuation
    text = re.sub(
        r"([!?.,])\1+",
        r"\1",
        text
    )

    return text.strip()


# ============================================================
# 4. TELUGU CHARACTER NORMALIZATION
# ============================================================

def normalize_telugu_characters(text):
    """
    Handle conservative character-level patterns
    that can occur in Telugu STT output.
    """

    patterns = [

        # Example:
        # కొణ్డపల్లి → కొండపల్లి
        (r"ణ్డ", "ండ"),

        # Similar conjunct variation
        (r"ణ్ఢ", "ంఢ"),
    ]

    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text)

    return text


# ============================================================
# 5. REPEATED CHARACTER NORMALIZATION
# ============================================================

def normalize_repeated_characters(text):
    """
    Remove excessive repeated Telugu vowel signs.
    """

    text = re.sub(r"ా{3,}", "ా", text)
    text = re.sub(r"ి{3,}", "ి", text)
    text = re.sub(r"ీ{3,}", "ీ", text)
    text = re.sub(r"ు{3,}", "ు", text)
    text = re.sub(r"ూ{3,}", "ూ", text)
    text = re.sub(r"ె{3,}", "ె", text)
    text = re.sub(r"ే{3,}", "ే", text)
    text = re.sub(r"ై{3,}", "ై", text)
    text = re.sub(r"ొ{3,}", "ొ", text)
    text = re.sub(r"ో{3,}", "ో", text)
    text = re.sub(r"ౌ{3,}", "ౌ", text)

    return text


# ============================================================
# 6. WORD-LEVEL CORRECTION
# ============================================================

def correct_known_words(text):
    """
    Correct recurring STT errors while preserving punctuation.
    """

    words = text.split()

    corrected_words = []

    for word in words:

        # Separate punctuation from the word.
        match = re.match(
            r'^([,.!?;:\'"()\-\u2013\u2014]*)(.*?)([,.!?;:\'"()\-\u2013\u2014]*)$',
            word
        )

        if match:

            prefix = match.group(1)
            core = match.group(2)
            suffix = match.group(3)

            if core in TELUGU_CORRECTIONS:
                core = TELUGU_CORRECTIONS[core]

            word = prefix + core + suffix

        corrected_words.append(word)

    return " ".join(corrected_words)


# ============================================================
# 7. WORD BOUNDARY NORMALIZATION
# ============================================================

def normalize_word_boundaries(text):
    """
    Normalize spacing around word boundaries.
    """

    # Normalize spaces around hyphens
    text = re.sub(
        r"\s*-\s*",
        "-",
        text
    )

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# 8. PUNCTUATION NORMALIZATION
# ============================================================

def normalize_punctuation(text):
    """
    Normalize punctuation spacing and repetition.
    """

    text = text.strip()

    if not text:
        return ""

    # Remove spaces before punctuation
    text = re.sub(
        r"\s+([,.!?;:])",
        r"\1",
        text
    )

    # Prevent excessive punctuation
    text = re.sub(r"!{2,}", "!", text)
    text = re.sub(r"\?{2,}", "?", text)
    text = re.sub(r"\.{2,}", ".", text)

    return text.strip()


# ============================================================
# 9. MAIN NORMALIZER
# ============================================================

def normalize_telugu(text):
    """
    Complete Telugu normalization pipeline.

    Raw STT
        ↓
    Unicode normalization
        ↓
    Basic cleanup
        ↓
    Telugu character normalization
        ↓
    Repeated character cleanup
        ↓
    Known STT correction
        ↓
    Word boundary cleanup
        ↓
    Punctuation normalization
        ↓
    Final Telugu
    """

    if not text:
        return ""

    # 1. Unicode
    text = normalize_unicode(text)

    # 2. General cleanup
    text = clean_text(text)

    # 3. Telugu character patterns
    text = normalize_telugu_characters(text)

    # 4. Repeated characters
    text = normalize_repeated_characters(text)

    # 5. Known STT mistakes
    text = correct_known_words(text)

    # 6. Word boundaries
    text = normalize_word_boundaries(text)

    # 7. Punctuation
    text = normalize_punctuation(text)

    return text


# ============================================================
# 10. TEST
# ============================================================

if __name__ == "__main__":

    test_sentences = [

        "ఇవి చేత్తో చేస్నా కొణ్డపల్లి బంబలు విటిన చక్కుతో చిక్కుతారు.",

        "ఇవి చేతితో చేసిన కొండపల్లి బొంబలో వీటిని చక్కతో చెక్కుతారు.",

        "రైతులు పొలంలో పనీ చేస్థున్నారు.",

        "అతను స్కూలుకి వెల్తున్నాడు.",

        "నాకు తెలుగు బాష చాల ఇష్టం.",
    ]

    for i, text in enumerate(test_sentences, 1):

        print("\n" + "=" * 60)
        print(f"TEST {i}")

        print("\nOriginal:")
        print(text)

        result = normalize_telugu(text)

        print("\nNormalized:")
        print(result)