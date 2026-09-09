from fastapi import UploadFile

from app.ai.audio.audio_processor import (
    validate_audio_file
)

from app.ai.transcription.transcription_service import (
    transcribe_audio
)

from app.ai.product_ai.product_extractor import (
    extract_product_information
)

from app.ai.product_ai.description_generator import (
    generate_product_description
)

from app.schemas.ai import (
    AIProductProcessingResponse
)


# =========================================
# PROCESS PRODUCT AUDIO
# =========================================

async def process_product_audio(
    audio_file: UploadFile
) -> AIProductProcessingResponse:
    """
    Complete AI pipeline for processing
    an artisan's product voice description.

    Pipeline:

    Audio
        ↓
    Audio Validation
        ↓
    Transcription
        ↓
    Product Information Extraction
        ↓
    Description Generation
        ↓
    Complete AI Response
    """

    # -------------------------------------
    # STEP 1: VALIDATE AUDIO
    # -------------------------------------

    await validate_audio_file(
        audio_file
    )

    # -------------------------------------
    # STEP 2: TRANSCRIBE AUDIO
    # -------------------------------------

    transcription_result = await transcribe_audio(
        audio_file
    )

    # -------------------------------------
    # STEP 3: EXTRACT PRODUCT INFORMATION
    # -------------------------------------

    extracted_product = (
        await extract_product_information(
            text=transcription_result.transcript,
            language=transcription_result.detected_language
        )
    )

    # -------------------------------------
    # STEP 4: GENERATE DESCRIPTION
    # -------------------------------------

    generated_description = (
        await generate_product_description(
            extracted_product
        )
    )

    # -------------------------------------
    # STEP 5: RETURN COMPLETE RESULT
    # -------------------------------------

    return AIProductProcessingResponse(
        transcript=transcription_result.transcript,

        processed_language=(
            transcription_result.detected_language
        ),

        extracted_product=extracted_product,

        ai_generated_description=(
            generated_description
        ),

        ai_suggested_category=(
            extracted_product.category
        ),

        # Real confidence calculation
        # will be added with the AI provider
        ai_confidence=None
    )