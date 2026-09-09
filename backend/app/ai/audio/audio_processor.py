from fastapi import UploadFile


# =========================================
# ALLOWED AUDIO TYPES
# =========================================

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/wav",
    "audio/x-wav",
    "audio/mp4",
    "audio/m4a",
    "audio/webm",
    "audio/ogg"
}


# Maximum audio file size: 25 MB
MAX_AUDIO_FILE_SIZE = 25 * 1024 * 1024


# =========================================
# VALIDATE AUDIO FILE
# =========================================

async def validate_audio_file(
    audio_file: UploadFile
) -> int:
    """
    Validate an uploaded audio file.

    Returns:
        int: Size of the validated file in bytes.

    Raises:
        ValueError: If the file is invalid.
    """

    # -------------------------------------
    # CHECK FILE TYPE
    # -------------------------------------

    if (
        audio_file.content_type
        not in ALLOWED_AUDIO_TYPES
    ):
        raise ValueError(
            "Unsupported audio file type"
        )

    # -------------------------------------
    # READ FILE CONTENT
    # -------------------------------------

    audio_content = await audio_file.read()

    file_size = len(audio_content)

    # -------------------------------------
    # CHECK FILE SIZE
    # -------------------------------------

    if file_size == 0:
        raise ValueError(
            "Audio file is empty"
        )

    if file_size > MAX_AUDIO_FILE_SIZE:
        raise ValueError(
            "Audio file exceeds the maximum allowed size of 25 MB"
        )

    # -------------------------------------
    # RESET FILE POINTER
    # -------------------------------------

    await audio_file.seek(0)

    return file_size