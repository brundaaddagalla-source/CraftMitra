# import subprocess
# from pathlib import Path


# def convert_to_wav(input_file, output_file=None):
#     """
#     Convert an audio/video file to a 16 kHz mono WAV file.

#     Supports formats such as:
#     MP3, MP4, M4A, FLAC, OGG, AAC, WAV, etc.
#     """

#     input_path = Path(input_file)

#     if not input_path.exists():
#         raise FileNotFoundError(
#             f"Input file not found: {input_path}"
#         )

#     # If output file is not specified,
#     # create <original_name>_converted.wav
#     if output_file is None:
#         output_file = input_path.with_name(
#             input_path.stem + "_converted.wav"
#         )

#     output_path = Path(output_file)

#     command = [
#         "ffmpeg",
#         "-y",
#         "-i", str(input_path),

#         # Convert to 16 kHz
#         "-ar", "16000",

#         # Convert to mono
#         "-ac", "1",

#         # 16-bit PCM WAV
#         "-sample_fmt", "s16",

#         str(output_path)
#     ]

#     try:
#         subprocess.run(
#             command,
#             check=True,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             text=True
#         )

#     except FileNotFoundError:
#         raise RuntimeError(
#             "FFmpeg is not installed or is not added to PATH. "
#             "Run 'ffmpeg -version' in the terminal to check."
#         )

#     except subprocess.CalledProcessError as e:
#         raise RuntimeError(
#             f"FFmpeg conversion failed:\n{e.stderr}"
#         )

#     print(f"Converted: {input_path} → {output_path}")

#     return str(output_path)


# if __name__ == "__main__":
#     # Test conversion directly
#     input_file = "telugu1.wav"

#     wav_file = convert_to_wav(input_file)

#     print("Output WAV:", wav_file)

import subprocess
from pathlib import Path


def convert_to_wav(
    input_file: str,
    output_file: str | None = None,
) -> str:
    """
    Convert an audio/video file to a 16 kHz mono WAV file.

    Supports formats such as:
    MP3, MP4, M4A, FLAC, OGG, AAC, WAV, etc.
    """

    input_path = Path(input_file)

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_path}"
        )

    # --------------------------------------------------------
    # Output path
    # --------------------------------------------------------

    if output_file is None:
        output_path = input_path.with_name(
            input_path.stem + "_converted.wav"
        )
    else:
        output_path = Path(output_file)

    # Make sure the parent directory exists.
    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # FFmpeg command
    # --------------------------------------------------------

    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),

        # 16 kHz
        "-ar",
        "16000",

        # Mono
        "-ac",
        "1",

        # 16-bit PCM WAV
        "-sample_fmt",
        "s16",

        str(output_path),
    ]

    # --------------------------------------------------------
    # Run FFmpeg
    # --------------------------------------------------------

    try:

        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    except FileNotFoundError as error:

        raise RuntimeError(
            "FFmpeg is not installed or is not available "
            "in PATH. Run 'ffmpeg -version' to verify."
        ) from error

    except subprocess.CalledProcessError as error:

        error_message = (
            error.stderr.strip()
            if error.stderr
            else "Unknown FFmpeg error."
        )

        raise RuntimeError(
            f"FFmpeg conversion failed: {error_message}"
        ) from error

    # --------------------------------------------------------
    # Verify output
    # --------------------------------------------------------

    if not output_path.exists():
        raise RuntimeError(
            "FFmpeg completed but the output WAV file "
            "was not created."
        )

    if output_path.stat().st_size == 0:
        raise RuntimeError(
            "FFmpeg created an empty WAV file."
        )

    return str(output_path)


# ------------------------------------------------------------
# Standalone test
# ------------------------------------------------------------

if __name__ == "__main__":

    input_file = "telugu1.wav"

    wav_file = convert_to_wav(
        input_file,
    )

    print("Output WAV:", wav_file)