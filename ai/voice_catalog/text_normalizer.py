import re
import unicodedata


# ============================================================
# 1. KNOWN STT CORRECTIONS
# ============================================================
#
# IMPORTANT:
# This is only one layer of the normalizer.
# It should contain recurring errors observed from your STT.
#
# Do NOT try to put the entire Telugu vocabulary here.
# ============================================================

TELUGU_CORRECTIONS = {

    "చేత్తో": "చేతితో",
    "చేస్నా": "చేసిన",
    "కొణ్డపల్లి": "కొండపల్లి",
    "బంబలు": "బొమ్మలు",
    "విటిన": "వీటిని",
    "చక్కుతో": "చెక్కుతో",
    "చిక్కుతారు": "చెక్కుతారు",

}


# ============================================================
# 2. UNICODE NORMALIZATION
# ============================================================

def normalize_unicode(text):
    """
    Convert equivalent Unicode representations into
    a standard NFC representation.
    """

    return unicodedata.normalize("NFC", text)


# ============================================================
# 3. BASIC TEXT CLEANING
# ============================================================

def clean_text(text):
    """
    General text cleanup.

    This works for arbitrary Telugu text and does not depend
    on specific words.
    """

    # Remove leading/trailing whitespace
    text = text.strip()

    # Replace multiple spaces/newlines/tabs with one space
    text = re.sub(r"\s+", " ", text)

    # Remove spaces before punctuation
    text = re.sub(r"\s+([,.!?;:])", r"\1", text)

    # Add space after punctuation when missing
    text = re.sub(r"([,.!?;:])(?=\S)", r"\1 ", text)

    # Remove repeated punctuation
    text = re.sub(r"([!?.,])\1+", r"\1", text)

    return text.strip()


# ============================================================
# 4. TELUGU-SPECIFIC CHARACTER NORMALIZATION
# ============================================================

def normalize_telugu_characters(text):
    """
    Handle character-level patterns that can occur in
    Telugu STT output.

    These rules are intentionally conservative.
    """

    patterns = [

        # Common nasal/conjunct variation
        (r"ణ్డ", "ండ"),
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
    Remove excessive repetition that can occur in STT output.
    """

    # Repeated Telugu vowel signs
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
    Correct recurring STT errors.

    This is deliberately kept separate from the general
    normalization logic.
    """

    words = text.split()

    corrected_words = []

    for word in words:

        # Separate punctuation from the actual word
        match = re.match(
            r"^([,.!?;:'\"()\-]*)(.*?)([,.!?;:'\"()\-]*)$",
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

    # Normalize spaces around hyphens
    text = re.sub(r"\s*-\s*", "-", text)

    # Normalize whitespace again
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# 8. PUNCTUATION NORMALIZATION
# ============================================================

def normalize_punctuation(text):

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

    Pipeline:

        Raw STT text
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
        Punctuation cleanup
              ↓
        Final normalized text
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
# TEST
# ============================================================

if __name__ == "__main__":

    text = (
        "ఇవి చేత్తో చేస్నా కొణ్డపల్లి "
        "బంబలు విటిన చక్కుతో చిక్కుతారు"
    )

    print("\n--- Original ---")
    print(text)

    corrected = normalize_telugu(text)

    print("\n--- Normalized ---")
    print(corrected)