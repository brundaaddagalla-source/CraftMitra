# import torch
# import librosa
# from transformers import AutoProcessor, AutoModelForCTC

# MODEL_NAME = "swechatelangana/swecha-gonthuka-asr"

# processor = AutoProcessor.from_pretrained(MODEL_NAME)
# model = AutoModelForCTC.from_pretrained(MODEL_NAME)

# device = "cpu"
# model = model.to(device)
# model.eval()


# def speech_to_text(audio_path):

#     audio, sr = librosa.load(
#         audio_path,
#         sr=16000
#     )

#     inputs = processor(
#         audio,
#         sampling_rate=16000,
#         return_tensors="pt"
#     )

#     inputs = {
#         key: value.to(device)
#         for key, value in inputs.items()
#     }

#     with torch.no_grad():
#         logits = model(**inputs).logits

#     predicted_ids = torch.argmax(logits, dim=-1)

#     text = processor.batch_decode(
#         predicted_ids
#     )[0]

#     return {
#         "text": text.strip(),
#         "language": "te"
#     }


# if __name__ == "__main__":

#     result = speech_to_text("telugu1.wav")

#     print("Speech to Text:")
#     print(result["text"])

import torch
import soundfile as sf
from transformers import AutoModel


MODEL_NAME = "ai4bharat/indic-conformer-600m-multilingual"

device = "cuda" if torch.cuda.is_available() else "cpu"

print("Using device:", device)
print("Loading IndicConformer...")

model = AutoModel.from_pretrained(
    MODEL_NAME,
    trust_remote_code=True
)

model = model.to(device)
model.eval()

print("IndicConformer loaded successfully.")


def speech_to_text(audio_path, language="te"):

    # --------------------------------------------------
    # Load WAV using soundfile
    # --------------------------------------------------
    audio, sample_rate = sf.read(
        audio_path,
        dtype="float32"
    )

    # --------------------------------------------------
    # Stereo → Mono
    # --------------------------------------------------
    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)

    # --------------------------------------------------
    # Resample to 16 kHz
    # --------------------------------------------------
    if sample_rate != 16000:

        import librosa

        audio = librosa.resample(
            audio,
            orig_sr=sample_rate,
            target_sr=16000
        )

        sample_rate = 16000

    # --------------------------------------------------
    # Convert NumPy → PyTorch
    # --------------------------------------------------
    wav = torch.tensor(
        audio,
        dtype=torch.float32
    )

    # Add batch/channel dimension
    wav = wav.unsqueeze(0)

    wav = wav.to(device)

    # --------------------------------------------------
    # IndicConformer inference
    # --------------------------------------------------
    with torch.no_grad():

        transcription = model(
            wav,
            language,
            "ctc"
        )

    return transcription


if __name__ == "__main__":

    result = speech_to_text(
        "telugu1.wav",
        "te"
    )

    print("\n--- Speech to Text ---")
    print(result)