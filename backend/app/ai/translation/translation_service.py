# # =========================================
# # TRANSLATION SERVICE FOUNDATION
# # =========================================

# async def translate_text(
#     text: str,
#     source_language: str | None = None,
#     target_language: str = "English"
# ) -> str:
#     """
#     Translate text from the source language
#     into the target language.

#     This is currently a provider-independent
#     translation service foundation.

#     A real translation model/provider will
#     be integrated later.
#     """

#     if not text or not text.strip():
#         raise ValueError(
#             "Text to translate cannot be empty"
#         )

#     raise NotImplementedError(
#         "No translation provider has been configured yet"
#     )

from ai.voice_catalog.translation import (
    translate_to_english,
    translate_to_hindi,
)


def translate_telugu_text(text: str) -> dict[str, str]:
    if not text or not text.strip():
        raise ValueError("Text to translate cannot be empty")

    english = translate_to_english(
        text.strip(),
        "te"
    )

    hindi = translate_to_hindi(
        english
    ) if english else ""

    return {
        "english": english.strip(),
        "hindi": hindi.strip(),
    }