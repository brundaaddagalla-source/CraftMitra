from file_converter import convert_to_wav
from speech_to_text import speech_to_text
from text_normalizer import normalize_telugu
from translation import (
    translate_to_english,
    translate_to_hindi
)


# ============================================================
# INPUT FILE
# ============================================================

# Supported:
# MP3, MP4, M4A, FLAC, OGG, WAV, etc.

audio_file = "telugu4.ogg"


# ============================================================
# FILE CONVERSION
# ============================================================

print("=" * 60)
print("FILE CONVERSION")
print("=" * 60)

wav_file = convert_to_wav(
    audio_file
)

print("WAV file:", wav_file)


# ============================================================
# SPEECH TO TEXT
# ============================================================

print("\n" + "=" * 60)
print("SPEECH TO TEXT")
print("=" * 60)

raw_text = speech_to_text(
    wav_file,
    "te"
)

print("\nRaw Telugu:")
print(raw_text)


# ============================================================
# TELUGU NORMALIZATION
# ============================================================

print("\n" + "=" * 60)
print("TELUGU NORMALIZATION")
print("=" * 60)

normalized_text = normalize_telugu(
    raw_text
)

print("\nNormalized Telugu:")
print(normalized_text)


# ============================================================
# TELUGU → ENGLISH
# ============================================================

print("\n" + "=" * 60)
print("TELUGU → ENGLISH")
print("=" * 60)

english_text = translate_to_english(
    normalized_text,
    "te"
)

print("\nEnglish:")
print(english_text)


# ============================================================
# ENGLISH → HINDI
# ============================================================

print("\n" + "=" * 60)
print("ENGLISH → HINDI")
print("=" * 60)

hindi_text = translate_to_hindi(
    english_text
)

print("\nHindi:")
print(hindi_text)


# ============================================================
# FINAL RESULT
# ============================================================

print("\n" + "=" * 60)
print("FINAL RESULT")
print("=" * 60)

print("\nRaw Telugu:")
print(raw_text)

print("\nNormalized Telugu:")
print(normalized_text)

print("\nEnglish:")
print(english_text)

print("\nHindi:")
print(hindi_text)

print("\n" + "=" * 60)
print("PIPELINE COMPLETED")
print("=" * 60)