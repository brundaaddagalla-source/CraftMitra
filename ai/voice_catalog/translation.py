import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM


# ============================================================
# MODEL
# ============================================================

MODEL_NAME = "facebook/nllb-200-distilled-600M"


# ============================================================
# DEVICE
# ============================================================

device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Using device: {device}")


# ============================================================
# LOAD MODEL
# ============================================================

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME
)

model = AutoModelForSeq2SeqLM.from_pretrained(
    MODEL_NAME
)

model = model.to(device)

model.eval()


# ============================================================
# LANGUAGE CODES
# ============================================================

LANGUAGE_CODES = {
    "te": "tel_Telu",
    "hi": "hin_Deva",
    "en": "eng_Latn"
}


# ============================================================
# TRANSLATION
# ============================================================

def translate_to_english(text, source_language):

    if not text:
        return ""

    # Already English
    if source_language == "en":
        return text

    if source_language not in LANGUAGE_CODES:
        raise ValueError(
            f"Unsupported language: {source_language}"
        )

    source_code = LANGUAGE_CODES[source_language]

    tokenizer.src_lang = source_code

    inputs = tokenizer(
        text,
        return_tensors="pt",
        padding=True,
        truncation=True
    )

    inputs = {
        key: value.to(device)
        for key, value in inputs.items()
    }

    # Generate English translation
    with torch.no_grad():

        translated_tokens = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.convert_tokens_to_ids(
                "eng_Latn"
            ),
            max_length=256
        )

    translated_text = tokenizer.batch_decode(
        translated_tokens,
        skip_special_tokens=True
    )[0]

    return translated_text.strip()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    telugu_text = "ఇవి చేతితో తయారు చేసిన కొండపల్లి బొమ్మలు."

    english = translate_to_english(
        telugu_text,
        "te"
    )

    print("\n--- Telugu ---")
    print(telugu_text)

    print("\n--- English ---")
    print(english)