"""
Uploads binary files (product photos, audio clips, etc.) to Supabase
Storage and returns a public URL that can be saved on a model
(e.g. ProductImage.image_url).

Requires SUPABASE_URL, SUPABASE_KEY and SUPABASE_BUCKET to be set in
the backend .env file, and the `supabase` package to be installed:

    pip install supabase
"""

import uuid
from functools import lru_cache

from fastapi import HTTPException, status

from app.core.config import settings


# =========================================
# SUPABASE CLIENT
# =========================================

@lru_cache
def _get_client():
    """
    Lazily create (and cache) the Supabase client so importing this
    module never fails just because Supabase isn't configured yet -
    the error only surfaces when an upload is actually attempted.
    """

    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        raise RuntimeError(
            "Supabase is not configured. Set SUPABASE_URL and "
            "SUPABASE_KEY in the backend .env file."
        )

    try:
        from supabase import create_client
    except ImportError as error:
        raise RuntimeError(
            "The 'supabase' package is not installed. "
            "Run: pip install supabase"
        ) from error

    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


# =========================================
# UPLOAD A FILE
# =========================================

def upload_file(
    file_bytes: bytes,
    original_filename: str,
    content_type: str | None,
    folder: str = "product-images",
) -> str:
    """
    Upload raw bytes to the configured Supabase bucket and return the
    public URL of the uploaded object.

    A random UUID is used as the stored filename (keeping the original
    extension) so two artisans uploading "photo.jpg" at the same time
    never collide.
    """

    if not settings.SUPABASE_BUCKET:
        raise RuntimeError(
            "SUPABASE_BUCKET is not configured in the backend .env file."
        )

    extension = ""
    if original_filename and "." in original_filename:
        extension = "." + original_filename.rsplit(".", 1)[-1].lower()

    object_path = f"{folder}/{uuid.uuid4().hex}{extension}"

    client = _get_client()

    try:
        client.storage.from_(settings.SUPABASE_BUCKET).upload(
            object_path,
            file_bytes,
            {"content-type": content_type} if content_type else None,
        )
    except RuntimeError:
        raise
    except Exception as error:  # supabase raises its own StorageException
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Failed to upload file to storage: {error}",
        ) from error

    public_url = client.storage.from_(
        settings.SUPABASE_BUCKET
    ).get_public_url(object_path)

    return public_url