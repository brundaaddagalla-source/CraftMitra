# from fastapi import UploadFile

# from app.ai.audio.audio_processor import (
#     validate_audio_file
# )

# from app.ai.transcription.transcription_service import (
#     transcribe_audio
# )

# from app.ai.product_ai.product_extractor import (
#     extract_product_information
# )

# from app.ai.product_ai.description_generator import (
#     generate_product_description
# )

# from app.schemas.ai import (
#     AIProductProcessingResponse
# )


# # =========================================
# # PROCESS PRODUCT AUDIO
# # =========================================

# async def process_product_audio(
#     audio_file: UploadFile
# ) -> AIProductProcessingResponse:
#     """
#     Complete AI pipeline for processing
#     an artisan's product voice description.

#     Pipeline:

#     Audio
#         ↓
#     Audio Validation
#         ↓
#     Transcription
#         ↓
#     Product Information Extraction
#         ↓
#     Description Generation
#         ↓
#     Complete AI Response
#     """

#     # -------------------------------------
#     # STEP 1: VALIDATE AUDIO
#     # -------------------------------------

#     await validate_audio_file(
#         audio_file
#     )

#     # -------------------------------------
#     # STEP 2: TRANSCRIBE AUDIO
#     # -------------------------------------

#     transcription_result = await transcribe_audio(
#         audio_file
#     )

#     # -------------------------------------
#     # STEP 3: EXTRACT PRODUCT INFORMATION
#     # -------------------------------------

#     extracted_product = (
#         await extract_product_information(
#             text=transcription_result.transcript,
#             language=transcription_result.detected_language
#         )
#     )

#     # -------------------------------------
#     # STEP 4: GENERATE DESCRIPTION
#     # -------------------------------------

#     generated_description = (
#         await generate_product_description(
#             extracted_product
#         )
#     )

#     # -------------------------------------
#     # STEP 5: RETURN COMPLETE RESULT
#     # -------------------------------------

#     return AIProductProcessingResponse(
#         transcript=transcription_result.transcript,

#         processed_language=(
#             transcription_result.detected_language
#         ),

#         extracted_product=extracted_product,

#         ai_generated_description=(
#             generated_description
#         ),

#         ai_suggested_category=(
#             extracted_product.category
#         ),

#         # Real confidence calculation
#         # will be added with the AI provider
#         ai_confidence=None
#     )

import asyncio
import tempfile
from pathlib import Path

from fastapi import UploadFile

from app.ai.audio.audio_processor import validate_audio_file
from app.ai.product_ai.description_generator import generate_product_description
from app.ai.product_ai.product_extractor import extract_product_information
from ai.voice_catalog.file_converter import convert_to_wav
from ai.voice_catalog.text_normalizer import normalize_transcript
from ai.voice_catalog.translation import translate_to_english, translate_to_hindi
from app.ai.transcription.transcription_service import transcribe_wav_file
from app.schemas.ai import AIExtractedProductData, AIProductProcessingResponse


# Prevent multiple requests from loading/using the GPU models at the same time.
GPU_LOCK = asyncio.Lock()

# Spoken languages the voice pipeline currently knows how to handle.
# IndicConformer (speech-to-text) itself supports many more Indic
# languages, but our translation step (IndicTrans2 Telugu->English)
# only has a Telugu source path wired up, so we cap the accepted
# languages here to what actually produces a correct result end to
# end. English needs no Telugu->English step at all - it's already
# the "english" output, so only the English->Hindi leg runs.
SUPPORTED_SPOKEN_LANGUAGES = {"te", "en"}


def run_voice_pipeline(wav_path: str, language: str = "te") -> dict[str, str]:
    """
    Run the CraftMitra voice-catalog AI pipeline for the given
    spoken language:

    WAV
      -> Speech-to-text (in `language`)
      -> Normalization (regional text)
      -> Translate to English (skipped if already English)
      -> Translate English -> Hindi
    """

    if language not in SUPPORTED_SPOKEN_LANGUAGES:
        raise ValueError(
            f"Unsupported spoken language '{language}'. "
            f"Supported languages: "
            f"{', '.join(sorted(SUPPORTED_SPOKEN_LANGUAGES))}."
        )

    # 1. Speech to text, in whatever language the artisan actually spoke
    transcription = transcribe_wav_file(
        wav_path,
        language
    )

    raw_transcript = transcription.transcript

    # 2. Normalize the transcript in that language
    regional_text = normalize_transcript(
        raw_transcript,
        language
    )

    if not regional_text:
        raise ValueError(
            "Transcript normalization returned empty text"
        )

    # 3. Translate to English (no-op if the artisan already spoke English)
    if language == "te":
        english = translate_to_english(regional_text, "te")
    else:
        english = regional_text

    # 4. Translate English -> Hindi
    hindi = translate_to_hindi(english) if english else ""

    return {
        "language": language,
        "raw_transcript": raw_transcript,
        "regional_text": regional_text,
        "english": english,
        "hindi": hindi,
    }


def _confidence_score(extracted: AIExtractedProductData) -> float:
    """
    Heuristic confidence: how much of the structured product data the
    (rule-based) extractor actually managed to fill in. This is not a
    real ML confidence score - there's no model backing this yet, just
    a proxy so the frontend has something to show/threshold on until
    there is one.
    """

    fields = [
        extracted.product_name,
        extracted.category,
        extracted.material,
        extracted.color,
        extracted.craft_technique,
    ]

    filled = sum(1 for value in fields if value)

    return round(filled / len(fields), 2)


async def process_product_audio(
    audio_file: UploadFile,
    language: str = "te",
) -> AIProductProcessingResponse:

    if language not in SUPPORTED_SPOKEN_LANGUAGES:
        raise ValueError(
            f"Unsupported spoken language '{language}'. "
            f"Supported languages: "
            f"{', '.join(sorted(SUPPORTED_SPOKEN_LANGUAGES))}."
        )

    # Validate uploaded audio
    await validate_audio_file(audio_file)

    # Preserve the original file extension
    suffix = (
        Path(audio_file.filename or "audio").suffix
        or ".bin"
    )

    try:
        with tempfile.TemporaryDirectory(
            prefix="craftmitra_voice_"
        ) as temp_dir:

            input_path = (
                Path(temp_dir) / f"input{suffix}"
            )

            wav_path = (
                Path(temp_dir) / "converted.wav"
            )

            # Read uploaded audio
            content = await audio_file.read()

            if not content:
                raise ValueError(
                    "Audio file is empty"
                )

            input_path.write_bytes(content)

            # Convert audio to 16 kHz mono WAV.
            # FFmpeg runs outside the GPU, so use a worker thread.
            await asyncio.to_thread(
                convert_to_wav,
                str(input_path),
                str(wav_path),
            )

            # The AI models use the GPU.
            # Only allow one voice pipeline to use them at a time.
            async with GPU_LOCK:

                result = await asyncio.to_thread(
                    run_voice_pipeline,
                    str(wav_path),
                    language,
                )

            # -------------------------------------
            # STRUCTURED EXTRACTION + DESCRIPTION
            # -------------------------------------
            # Runs on the English text (regardless of what the
            # artisan spoke) since that's the only language the
            # keyword/regex extractor below understands. It's
            # best-effort: if the transcript doesn't contain enough
            # to extract anything useful, the artisan just fills the
            # product details in manually on the review screen
            # instead of the request failing outright.

            extracted_product = None
            ai_generated_description = None
            ai_generated_description_hindi = None
            ai_suggested_category = None
            ai_confidence = None

            try:
                extracted_product = await extract_product_information(
                    result["english"],
                    "en",
                )

                ai_generated_description = await generate_product_description(
                    extracted_product
                )

                ai_suggested_category = extracted_product.category
                ai_confidence = _confidence_score(extracted_product)

                # Translate the generated description into Hindi too, so
                # the review screen can show it in regional / English /
                # Hindi. Uses the GPU (NLLB) - same lock as the rest of
                # the voice pipeline.
                async with GPU_LOCK:
                    ai_generated_description_hindi = await asyncio.to_thread(
                        translate_to_hindi,
                        ai_generated_description,
                    )

            except ValueError:
                pass

            return AIProductProcessingResponse(
                transcript=result["regional_text"],
                raw_transcript=result["raw_transcript"],
                regional_text=result["regional_text"],
                # Kept for older frontend builds that still read this
                # field name; only meaningful when the artisan spoke Telugu.
                normalized_telugu=(
                    result["regional_text"]
                    if result["language"] == "te"
                    else None
                ),
                processed_language=result["language"],

                english=result["english"],
                hindi=result["hindi"],

                extracted_product=extracted_product,
                ai_generated_description=ai_generated_description,
                ai_generated_description_hindi=ai_generated_description_hindi,
                ai_suggested_category=ai_suggested_category,
                ai_confidence=ai_confidence,
            )

    finally:
        # Reset the uploaded file pointer.
        await audio_file.seek(0)