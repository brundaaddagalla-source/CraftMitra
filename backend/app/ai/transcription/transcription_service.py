# from fastapi import UploadFile

# from app.schemas.ai import TranscriptionResponse


# # =========================================
# # TRANSCRIBE AUDIO
# # =========================================

# async def transcribe_audio(
#     audio_file: UploadFile
# ) -> TranscriptionResponse:
#     """
#     Transcribe an audio file into text.

#     This is currently a transcription service
#     interface/foundation.

#     A real AI speech-to-text provider will be
#     integrated later.
#     """

#     raise NotImplementedError(
#         "No transcription provider has been configured yet"
#     )

from pathlib import Path

from app.schemas.ai import TranscriptionResponse
from ai.voice_catalog.speech_to_text import speech_to_text


def transcribe_wav_file(
    audio_path: str,
    language: str = "te"
) -> TranscriptionResponse:

    if not audio_path:
        raise ValueError("Audio path is required")

    path = Path(audio_path)

    if not path.exists():
        raise ValueError("Converted audio file does not exist")

    result = speech_to_text(
        str(path),
        language
    )

    if isinstance(result, dict):
        text = str(
            result.get("text", "")
        ).strip()
    else:
        text = str(result).strip()

    if not text:
        raise ValueError(
            "Speech-to-text returned an empty transcript"
        )

    return TranscriptionResponse(
        transcript=text,
        detected_language=language
    )