from speech_to_text import speech_to_text
from text_normalizer import normalize_telugu
from translation import translate_to_english


# ============================================================
# INPUT
# ============================================================

audio_file = "telugu.mp4"


# ============================================================
# 1. SPEECH → TEXT
# ============================================================

result = speech_to_text(audio_file)

text = result["text"]
language = result["language"]


print("\n========================================")
print("          SPEECH TO TEXT")
print("========================================")

print(text)

print("\nDetected language:")
print(language)


# ============================================================
# 2. TEXT NORMALIZATION
# ============================================================

if language == "te":

    normalized_text = normalize_telugu(text)

else:

    # For Hindi/English etc. we currently don't normalize
    # using the Telugu normalizer.
    normalized_text = text


print("\n========================================")
print("          NORMALIZED TEXT")
print("========================================")

print(normalized_text)


# ============================================================
# 3. TRANSLATION
# ============================================================

english_text = translate_to_english(
    normalized_text,
    language
)


print("\n========================================")
print("             TRANSLATION")
print("========================================")

print(english_text)


# ============================================================
# FINAL RESULT
# ============================================================

final_result = {
    "speech_to_text": text,
    "normalized_text": normalized_text,
    "translation": english_text,
    "language": language
}


print("\n========================================")
print("           FINAL RESULT")
print("========================================")

print(final_result)