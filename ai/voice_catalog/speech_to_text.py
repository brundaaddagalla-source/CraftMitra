# import torch
# import soundfile as sf
# from transformers import AutoModel


# MODEL_NAME = "ai4bharat/indic-conformer-600m-multilingual"

# device = "cuda" if torch.cuda.is_available() else "cpu"

# print("Using device:", device)
# print("Loading IndicConformer...")

# model = AutoModel.from_pretrained(
#     MODEL_NAME,
#     trust_remote_code=True
# )

# model = model.to(device)
# model.eval()

# print("IndicConformer loaded successfully.")


# def speech_to_text(audio_path, language="te"):

#     # --------------------------------------------------
#     # Load WAV using soundfile
#     # --------------------------------------------------
#     audio, sample_rate = sf.read(
#         audio_path,
#         dtype="float32"
#     )

#     # --------------------------------------------------
#     # Stereo → Mono
#     # --------------------------------------------------
#     if len(audio.shape) > 1:
#         audio = audio.mean(axis=1)

#     # --------------------------------------------------
#     # Resample to 16 kHz
#     # --------------------------------------------------
#     if sample_rate != 16000:

#         import librosa

#         audio = librosa.resample(
#             audio,
#             orig_sr=sample_rate,
#             target_sr=16000
#         )

#         sample_rate = 16000

#     # --------------------------------------------------
#     # Convert NumPy → PyTorch
#     # --------------------------------------------------
#     wav = torch.tensor(
#         audio,
#         dtype=torch.float32
#     )

#     # Add batch/channel dimension
#     wav = wav.unsqueeze(0)

#     wav = wav.to(device)

#     # --------------------------------------------------
#     # IndicConformer inference
#     # --------------------------------------------------
#     with torch.no_grad():

#         transcription = model(
#             wav,
#             language,
#             "ctc"
#         )

#     return transcription


# if __name__ == "__main__":

#     result = speech_to_text(
#         "telugu1.wav",
#         "te"
#     )

#     print("\n--- Speech to Text ---")
#     print(result)

import torch
import soundfile as sf

from transformers import AutoModel


MODEL_NAME = "ai4bharat/indic-conformer-600m-multilingual"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print("Using device:", DEVICE)
print("Loading IndicConformer...")


model = AutoModel.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True,
)

model = model.to(DEVICE)
model.eval()

print("IndicConformer loaded successfully.")


def speech_to_text(
    audio_path: str,
    language: str = "te",
) -> dict[str, str]:

    if not audio_path:
        raise ValueError("Audio path is required")

    if not language:
        raise ValueError("Language is required")

    # --------------------------------------------------
    # Load WAV
    # --------------------------------------------------

    audio, sample_rate = sf.read(
        audio_path,
        dtype="float32",
    )

    # --------------------------------------------------
    # Stereo → Mono
    # --------------------------------------------------

    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)

    # --------------------------------------------------
    # Resample → 16 kHz
    # --------------------------------------------------

    if sample_rate != 16000:

        import librosa

        audio = librosa.resample(
            audio,
            orig_sr=sample_rate,
            target_sr=16000,
        )

        sample_rate = 16000

    # --------------------------------------------------
    # NumPy → PyTorch
    # --------------------------------------------------

    wav = torch.tensor(
        audio,
        dtype=torch.float32,
    )

    # --------------------------------------------------
    # Add batch dimension
    # --------------------------------------------------

    wav = wav.unsqueeze(0)

    wav = wav.to(DEVICE)

    # --------------------------------------------------
    # IndicConformer inference
    # --------------------------------------------------

    with torch.no_grad():

        transcription = model(
            wav,
            language,
            "ctc",
        )

    # --------------------------------------------------
    # Normalize model output
    # --------------------------------------------------

    if isinstance(transcription, dict):

        text = transcription.get(
            "text",
            "",
        )

    else:

        text = str(transcription)

    text = text.strip()

    if not text:
        raise ValueError(
            "IndicConformer returned an empty transcription"
        )

    # --------------------------------------------------
    # Stable API-facing result
    # --------------------------------------------------

    return {
        "text": text,
        "language": language,
    }


# ------------------------------------------------------
# Standalone testing
# ------------------------------------------------------

if __name__ == "__main__":

    result = speech_to_text(
        "telugu1.wav",
        "te",
    )

    print("\n--- Speech to Text ---")
    print("Language:", result["language"])
    print("Text:", result["text"])