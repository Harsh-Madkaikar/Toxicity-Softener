import os
import re
import pickle

from preprocess import preprocess_text
from softener import soften_text

NLP_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(NLP_DIR)
MODEL_DIR = os.path.join(BASE_DIR, "models")
TFIDF_PATH = os.path.join(MODEL_DIR, "tfidf_vectorizer.pkl")
TOXICITY_MODEL_PATH = os.path.join(MODEL_DIR, "toxicity_model.pkl")

POSITIVE_PATTERNS = [
    r"\bthank(?:s| you)\b", r"\bi appreciate\b", r"\bi love\b", r"\bi like\b",
    r"\blove this\b", r"\bgreat\b", r"\bamazing\b", r"\bawesome\b", r"\bexcellent\b",
    r"\bfantastic\b", r"\bwonderful\b", r"\bbrilliant\b", r"\bgood (?:job|work|idea|point)\b",
    r"\bgreat (?:job|work|idea|point)\b", r"\bwell done\b", r"\bnicely done\b",
    r"\bi agree\b", r"\byou(?:'re| are) right\b", r"\bvery helpful\b", r"\breally helpful\b",
    r"\bwell said\b", r"\bgood luck\b", r"\bbest wishes\b", r"\bhave a great day\b",
    r"\bproud of you\b", r"\bkeep it up\b", r"\bcongratulations\b", r"\bcongrats\b",
]

NEGATIVE_PATTERNS = [
    r"\b(?:you are|you're)\s+(?:an?\s+)?(?:idiot|moron|stupid|dumb|fool|clueless|useless|pathetic)\b",
    r"\b(?:your idea|your suggestion)\s+(?:is\s+)?(?:stupid|terrible|awful|ridiculous|useless|dumb)\b",
    r"\bthis is (?:a\s+)?(?:terrible|awful|stupid|ridiculous|useless)\b",
    r"\b(?:you clearly )?(?:don't|do not) understand\b",
    r"\byou have no (?:idea|clue)\b",
    r"\b(?:you don't|you do not) know what (?:you are|you're) talking about\b",
    r"\bstop wasting\b", r"\bwasting (?:everyone's|our|my) time\b",
    r"\b(?:shut up|fuck you|go to hell)\b",
    r"\bmakes no sense\b", r"\bdoesn't make sense\b", r"\bdoes not make sense\b",
    r"\b(?:stupid|idiot|moron|dumb|terrible|ridiculous|awful|pathetic|useless)\b",
]


def _matches(text, patterns):
    low = text.lower()
    return any(re.search(p, low) for p in patterns)


def is_clearly_positive(text):
    return _matches(text, POSITIVE_PATTERNS) and not _matches(text, NEGATIVE_PATTERNS)


def _probability_of_toxic_class(probabilities):
    try:
        classes = list(model.classes_)
        if 1 in classes:
            return float(probabilities[classes.index(1)])
        if "1" in classes:
            return float(probabilities[classes.index("1")])
    except Exception:
        pass
    return float(probabilities[-1])


if not os.path.exists(TFIDF_PATH):
    raise FileNotFoundError(f"TF-IDF vectorizer not found: {TFIDF_PATH}\nRun: python nlp/tfidf.py")
if not os.path.exists(TOXICITY_MODEL_PATH):
    raise FileNotFoundError(f"Toxicity model not found: {TOXICITY_MODEL_PATH}\nRun: python nlp/classifier.py")

with open(TFIDF_PATH, "rb") as f:
    vectorizer = pickle.load(f)
with open(TOXICITY_MODEL_PATH, "rb") as f:
    model = pickle.load(f)


def analyze_message(text):
    text = "" if text is None else str(text).strip()
    if not text:
        return {"original": "", "toxicity": "LOW", "toxicity_probability": 0.0, "action": "KEEP", "suggestion": ""}

    # Protect clearly positive comments from false positives in a word-based model.
    if is_clearly_positive(text):
        return {"original": text, "toxicity": "LOW", "toxicity_probability": 0.0, "action": "KEEP", "suggestion": text}

    cleaned = " ".join(preprocess_text(text))
    features = vectorizer.transform([cleaned])
    probabilities = model.predict_proba(features)[0]
    p = max(0.0, min(1.0, _probability_of_toxic_class(probabilities)))

    # Explicit toxic phrases should not be hidden by a poorly calibrated model.
    explicit_negative = _matches(text, NEGATIVE_PATTERNS)
    if explicit_negative:
        p = max(p, 0.75)

    if p < 0.40:
        level, action, suggestion = "LOW", "KEEP", text
    elif p <= 0.70:
        level, action, suggestion = "BORDERLINE", "OFFER_SOFTENING", soften_text(text)
    else:
        level, action, suggestion = "HIGH", "SOFTEN", soften_text(text)

    return {
        "original": text,
        "toxicity": level,
        "toxicity_probability": round(p, 3),
        "action": action,
        "suggestion": suggestion,
    }
