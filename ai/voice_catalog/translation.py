import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from IndicTransToolkit.processor import IndicProcessor


# ============================================================
# DEVICE
# ============================================================

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

print(f"Translation device: {DEVICE}")


# ============================================================
# ============================================================
# 1. INDIC TRANS 2
# TELUGU → ENGLISH
# ============================================================
# ============================================================

INDIC_MODEL = "ai4bharat/indictrans2-indic-en-1B"

print("\nLoading IndicTrans2 Telugu → English...")

indic_tokenizer = AutoTokenizer.from_pretrained(
    INDIC_MODEL,
    trust_remote_code=True
)

indic_model = AutoModelForSeq2SeqLM.from_pretrained(
    INDIC_MODEL,
    trust_remote_code=True,
    torch_dtype=(
        torch.float16
        if DEVICE == "cuda"
        else torch.float32
    )
).to(DEVICE)

indic_model.eval()

indic_processor = IndicProcessor(
    inference=True
)

SRC_LANG = "tel_Telu"
EN_LANG = "eng_Latn"

print("IndicTrans2 loaded successfully.")


# ============================================================
# TELUGU → ENGLISH FUNCTION
# ============================================================

def translate_to_english(
    text,
    source_language="te"
):

    if not text or not text.strip():
        return ""

    # --------------------------------------------------------
    # Check language
    # --------------------------------------------------------

    if source_language != "te":
        raise ValueError(
            "This translation function currently supports "
            "Telugu (te) as the source language."
        )

    # --------------------------------------------------------
    # IndicTrans2 language codes
    # --------------------------------------------------------

    src_lang = "tel_Telu"
    tgt_lang = "eng_Latn"

    # --------------------------------------------------------
    # Preprocess using official IndicTransToolkit
    # --------------------------------------------------------

    batch = indic_processor.preprocess_batch(
        [text],
        src_lang=src_lang,
        tgt_lang=tgt_lang
    )

    # --------------------------------------------------------
    # Tokenize
    # --------------------------------------------------------

    inputs = indic_tokenizer(
        batch,
        padding="longest",
        truncation=True,
        max_length=256,
        return_tensors="pt"
    ).to(DEVICE)

    # --------------------------------------------------------
    # Generate
    # --------------------------------------------------------

    with torch.inference_mode():

        generated_tokens = indic_model.generate(
            **inputs,
            num_beams=5,
            max_length=256
        )

    # --------------------------------------------------------
    # Decode
    # --------------------------------------------------------

    decoded = indic_tokenizer.batch_decode(
        generated_tokens,
        skip_special_tokens=True
    )

    # --------------------------------------------------------
    # Postprocess
    # --------------------------------------------------------

    english = indic_processor.postprocess_batch(
        decoded,
        lang=tgt_lang
    )[0]

    return english.strip()


# ============================================================
# ============================================================
# 2. NLLB
# ENGLISH → HINDI
# ============================================================
# ============================================================

NLLB_MODEL = "facebook/nllb-200-distilled-600M"

print("\nLoading NLLB English → Hindi...")

nllb_tokenizer = AutoTokenizer.from_pretrained(
    NLLB_MODEL
)

nllb_model = AutoModelForSeq2SeqLM.from_pretrained(
    NLLB_MODEL,
    torch_dtype=(
        torch.float16
        if DEVICE == "cuda"
        else torch.float32
    )
).to(DEVICE)

nllb_model.eval()

print("NLLB loaded successfully.")


# ============================================================
# ENGLISH → HINDI FUNCTION
# ============================================================

def translate_to_hindi(text):

    if not text or not text.strip():
        return ""

    # --------------------------------------------------------
    # Source language
    # --------------------------------------------------------

    nllb_tokenizer.src_lang = "eng_Latn"

    # --------------------------------------------------------
    # Tokenize
    # --------------------------------------------------------

    inputs = nllb_tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=256
    ).to(DEVICE)

    # --------------------------------------------------------
    # Hindi language token
    # --------------------------------------------------------

    hindi_token_id = nllb_tokenizer.convert_tokens_to_ids(
        "hin_Deva"
    )

    # --------------------------------------------------------
    # Generate
    # --------------------------------------------------------

    with torch.inference_mode():

        generated_tokens = nllb_model.generate(
            **inputs,
            forced_bos_token_id=hindi_token_id,
            max_length=256,
            num_beams=5
        )

    # --------------------------------------------------------
    # Decode
    # --------------------------------------------------------

    hindi = nllb_tokenizer.batch_decode(
        generated_tokens,
        skip_special_tokens=True
    )[0]

    return hindi.strip()


# ============================================================
# COMPLETE TELUGU → ENGLISH → HINDI
# ============================================================

def translate_telugu(text):

    if not text or not text.strip():
        return {
            "english": "",
            "hindi": ""
        }

    # Telugu → English
    english = translate_to_english(
        text,
        "te"
    )

    # English → Hindi
    hindi = translate_to_hindi(
        english
    )

    return {
        "english": english,
        "hindi": hindi
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    telugu_text = (
        "ఈ చీరను నేను నా సొంత చేతులతోనే చేశాను "
        "వారం రోజులు పట్టింది చేయడానికి. "
        "ఈ చీర మీద ఉన్న ప్రతి బొమ్మ నేను నా చేతులతో "
        "గీసి రంగులు వేశాను"
    )

    print("\n" + "=" * 60)
    print("TRANSLATION TEST")
    print("=" * 60)

    print("\nTelugu:")
    print(telugu_text)

    # --------------------------------------------------------
    # Telugu → English
    # --------------------------------------------------------

    english = translate_to_english(
        telugu_text,
        "te"
    )

    print("\nEnglish:")
    print(english)

    # --------------------------------------------------------
    # English → Hindi
    # --------------------------------------------------------

    hindi = translate_to_hindi(
        english
    )

    print("\nHindi:")
    print(hindi)