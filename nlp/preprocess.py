import re


def preprocess_text(text):
    if text is None:
        return []
    text = str(text).replace("\u200b", " ").strip().lower()
    text = re.sub(r"https?://\S+|www\.\S+", " URL ", text)
    text = re.sub(r"\S+@\S+", " EMAIL ", text)
    text = re.sub(r"[^a-z0-9'!?.,\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.split() if text else []
