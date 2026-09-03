import re

# Phrase-level rewrites are deliberately specific so different inputs
# produce different, context-relevant suggestions instead of one fixed reply.
PHRASE_RULES = [
    (r"\b(?:you are|you're)\s+(?:an?\s+)?(?:idiot|moron|stupid|dumb|fool|clueless)\b",
     "I don't agree with that perspective"),
    (r"\b(?:you are|you're)\s+(?:useless|pathetic|ridiculous)\b",
     "I have some concerns about this approach"),
    (r"\b(?:your idea|your suggestion|this idea)\s+(?:is\s+)?(?:stupid|terrible|awful|ridiculous|useless|dumb)\b",
     "I have some concerns about this idea"),
    (r"\bthis is (?:a\s+)?(?:terrible|awful|stupid|ridiculous)\s+(idea|solution|approach|suggestion)\b",
     r"I have some concerns about this \1"),
    (r"\b(?:you clearly )?(?:don't|do not) understand\b",
     "I think there may be a misunderstanding"),
    (r"\byou have no (?:idea|clue)\b",
     "I think we may have different understandings"),
    (r"\b(?:you don't|you do not) know what (?:you are|you're) talking about\b",
     "I have a different understanding of the topic"),
    (r"\bstop wasting (?:everyone's|our|my) time\b",
     "Could we focus on the key issue to use our time effectively"),
    (r"\bwhat (?:a|an) (?:ridiculous|stupid|awful|terrible) (idea|proposal|suggestion)\b",
     r"I don't think this \1 is the best option"),
]

WORD_REPLACEMENTS = {
    "stupid": "unhelpful",
    "idiot": "unhelpful",
    "moron": "unhelpful",
    "dumb": "ineffective",
    "terrible": "not ideal",
    "awful": "not effective",
    "ridiculous": "unconvincing",
    "pathetic": "not effective",
    "useless": "not particularly useful",
    "hate": "strongly dislike",
}


def soften_text(text):
    original = str(text or "").strip()
    if not original:
        return ""

    result = original

    for pattern, replacement in PHRASE_RULES:
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    # Replace remaining toxic words while preserving the rest of the sentence.
    for bad, good in WORD_REPLACEMENTS.items():
        result = re.sub(rf"\b{re.escape(bad)}\b", good, result, flags=re.IGNORECASE)

    # Make common imperative/aggressive openings more constructive.
    result = re.sub(r"^\s*shut up\b", "I think it would be better to focus on the discussion", result, flags=re.I)
    result = re.sub(r"^\s*stop\s+being\s+", "Could we avoid being ", result, flags=re.I)

    # If a toxic model fires but no lexical rule changed the text, give a
    # sentence-specific constructive wrapper rather than a repeated canned line.
    if result == original:
        if re.search(r"\byou\b", original, re.I):
            return "I see the issue differently, and I think we could discuss it more constructively."
        if re.search(r"\b(?:idea|approach|solution|proposal|suggestion)\b", original, re.I):
            return "I have some concerns about this approach. Perhaps we could consider an alternative."
        return "I disagree with this point, but I'd like to discuss the reasoning constructively."

    # Capitalize the first character if a replacement changed it awkwardly.
    return result[:1].upper() + result[1:] if result else original
