# from fastapi import (
#     APIRouter,
#     File,
#     HTTPException,
#     UploadFile
# )

# from app.schemas.ai import (
#     AIProductProcessingResponse
# )

# from app.services.ai_product_pipeline_service import (
#     process_product_audio
# )


# router = APIRouter(
#     prefix="/ai",
#     tags=["AI"]
# )


# # =========================================
# # PROCESS PRODUCT AUDIO
# # =========================================

# @router.post(
#     "/process-product-audio",
#     response_model=AIProductProcessingResponse
# )
# async def process_product_audio_endpoint(
#     audio_file: UploadFile = File(...)
# ):
#     """
#     Process an artisan's product voice description.

#     Current pipeline:

#     Audio
#         ↓
#     Validation
#         ↓
#     Transcription
#         ↓
#     Product Information Extraction
#         ↓
#     Description Generation
#         ↓
#     Complete AI Product Result
#     """

#     try:
#         result = await process_product_audio(
#             audio_file
#         )

#         return result

#     except ValueError as error:
#         raise HTTPException(
#             status_code=400,
#             detail=str(error)
#         )

#     except NotImplementedError as error:
#         raise HTTPException(
#             status_code=501,
#             detail=str(error)
#         )

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.ai import AIProductProcessingResponse
from app.services.ai_product_pipeline_service import process_product_audio


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post(
    "/process-product-audio",
    response_model=AIProductProcessingResponse,
)
async def process_product_audio_endpoint(
    audio_file: UploadFile = File(...),
):
    try:
        return await process_product_audio(audio_file)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    except RuntimeError as error:
        raise HTTPException(
            status_code=500,
            detail=f"AI processing failed: {error}",
        ) from error