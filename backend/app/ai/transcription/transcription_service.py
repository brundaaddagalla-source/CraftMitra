from fastapi import UploadFile

from app.schemas.ai import TranscriptionResponse


# =========================================
# TRANSCRIBE AUDIO
# =========================================

async def transcribe_audio(
    audio_file: UploadFile
) -> TranscriptionResponse:
    """
    Transcribe an audio file into text.

    This is currently a transcription service
    interface/foundation.

    A real AI speech-to-text provider will be
    integrated later.
    """

    raise NotImplementedError(
        "No transcription provider has been configured yet"
    )