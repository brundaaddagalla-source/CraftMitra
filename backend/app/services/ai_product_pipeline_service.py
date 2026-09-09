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
from ai.voice_catalog.file_converter import convert_to_wav
from ai.voice_catalog.text_normalizer import normalize_telugu
from app.ai.transcription.transcription_service import transcribe_wav_file
from app.ai.translation.translation_service import translate_telugu_text
from app.schemas.ai import AIProductProcessingResponse


# Prevent multiple requests from loading/using the GPU models at the same time.
GPU_LOCK = asyncio.Lock()


def run_voice_pipeline(wav_path: str) -> dict[str, str]:
    """
    Run the existing CraftMitra voice-catalog AI pipeline:

    WAV
      -> Speech-to-text
      -> Telugu normalization
      -> Telugu -> English
      -> English -> Hindi
    """

    # 1. Speech to text
    transcription = transcribe_wav_file(
        wav_path,
        "te"
    )

    raw_telugu = transcription.transcript

    # 2. Normalize Telugu
    normalized_telugu = normalize_telugu(
        raw_telugu
    )

    if not normalized_telugu:
        raise ValueError(
            "Telugu normalization returned empty text"
        )

    # 3. Translate Telugu -> English
    # 4. Translate English -> Hindi
    translations = translate_telugu_text(
        normalized_telugu
    )

    return {
        "raw_telugu": raw_telugu,
        "normalized_telugu": normalized_telugu,
        "english": translations["english"],
        "hindi": translations["hindi"],
    }


async def process_product_audio(
    audio_file: UploadFile,
) -> AIProductProcessingResponse:

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
                )

            return AIProductProcessingResponse(
                transcript=result["normalized_telugu"],
                raw_transcript=result["raw_telugu"],
                normalized_telugu=result["normalized_telugu"],
                processed_language="te",

                english=result["english"],
                hindi=result["hindi"],

                # These are not implemented yet.
                extracted_product=None,
                ai_generated_description=None,
                ai_suggested_category=None,
                ai_confidence=None,
            )

    finally:
        # Reset the uploaded file pointer.
        await audio_file.seek(0)