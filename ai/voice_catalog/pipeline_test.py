from speech_to_text import speech_to_text
from text_normalizer import normalize_telugu
from translation import translate_to_english


audio_file = "telugu1.wav"


print("=" * 60)
print("SPEECH TO TEXT")
print("=" * 60)

raw_text = speech_to_text(
    audio_file,
    "te"
)

print(raw_text)


print("\n" + "=" * 60)
print("TELUGU NORMALIZATION")
print("=" * 60)

normalized_text = normalize_telugu(raw_text)

print(normalized_text)


print("\n" + "=" * 60)
print("TRANSLATION")
print("=" * 60)

english_text = translate_to_english(
    normalized_text,
    "te"
)

print(english_text)


print("\n" + "=" * 60)
print("FINAL RESULT")
print("=" * 60)

print("Raw Telugu:")
print(raw_text)

print("\nNormalized Telugu:")
print(normalized_text)

print("\nEnglish:")
print(english_text)