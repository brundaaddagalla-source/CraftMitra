"""
Bridges the AI image-enhancement pipeline (ai/image_enhancement/) to a
stored ProductImage row.

This runs as a FastAPI background task, kicked off right after
`POST /{image_id}/enhance` marks the image as "processing":

    download original image bytes (from Supabase)
        -> decode to a NumPy array
        -> run the enhancement pipeline
        -> encode the result back to bytes
        -> upload to Supabase
        -> persist enhanced_image_url (status -> "completed")

Any failure along the way marks the image as "failed" instead of
leaving it stuck on "processing" forever.
"""

import logging

import requests

from app.database import SessionLocal
from app.services import product_image_service, storage_service

logger = logging.getLogger("uvicorn.error")


def run_enhancement_pipeline(image_id: int) -> None:
    """
    Runs in a background task (its own thread), so it needs its own
    DB session rather than reusing the one from the original request
    (that session is closed by the time this runs).
    """

    db = SessionLocal()

    try:
        image = product_image_service.get_product_image_by_id(db, image_id)

        if not image:
            logger.error(
                "Enhancement pipeline: image %s no longer exists", image_id
            )
            return

        # -------------------------------------
        # 1. DOWNLOAD THE ORIGINAL IMAGE
        # -------------------------------------

        response = requests.get(image.image_url, timeout=30)
        response.raise_for_status()
        original_bytes = response.content

        # -------------------------------------
        # 2. DECODE TO A NUMPY ARRAY
        # -------------------------------------
        #
        # Imported lazily so that a broken/missing dependency here
        # (opencv, backgroundremover, ...) can't prevent the rest of
        # the API from starting up - same defensive approach as the
        # /ai voice routes in main.py.

        import cv2
        import numpy as np

        from ai.image_enhancement.image_enhancement_pipeline import (
            enhance_image,
        )

        file_bytes = np.frombuffer(original_bytes, dtype=np.uint8)
        original_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if original_image is None:
            raise ValueError("Could not decode downloaded image")

        # -------------------------------------
        # 3. RUN THE ENHANCEMENT PIPELINE
        # -------------------------------------

        result = enhance_image(original_image)

        if not result.get("success"):
            raise RuntimeError("Enhancement pipeline reported failure")

        final_image = result["final_image"]

        # -------------------------------------
        # 4. ENCODE + UPLOAD THE RESULT
        # -------------------------------------

        success, encoded = cv2.imencode(".jpg", final_image)

        if not success:
            raise IOError("Could not encode enhanced image")

        enhanced_url = storage_service.upload_file(
            encoded.tobytes(),
            "enhanced.jpg",
            "image/jpeg",
            folder="enhanced-images",
        )

        # -------------------------------------
        # 5. PERSIST THE RESULT
        # -------------------------------------

        product_image_service.save_enhanced_image(db, image, enhanced_url)

        logger.info("Enhancement completed for image %s", image_id)

    except Exception:
        logger.exception("Enhancement pipeline failed for image %s", image_id)

        try:
            image = product_image_service.get_product_image_by_id(db, image_id)
            if image and image.processing_status == "processing":
                product_image_service.mark_image_processing_failed(db, image)
        except Exception:
            logger.exception(
                "Also failed to mark image %s as failed", image_id
            )

    finally:
        db.close()