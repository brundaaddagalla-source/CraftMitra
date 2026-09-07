from faster_whisper import WhisperModel


model = WhisperModel(
    "tiny",
    device="cpu",
    compute_type="int8"
)


def speech_to_text(audio_path):
    segments, info = model.transcribe(audio_path, vad_filter=True)

    text = " ".join(segment.text for segment in segments)

    return {
        "text": text.strip(),
        "language": info.language
    }


if __name__ == "__main__":
    result = speech_to_text("telugu.mp4")
    print(result)