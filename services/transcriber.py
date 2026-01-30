import re
from typing import List


def restore_punctuation(text: str) -> str:
    text = text.strip()
    text = re.sub(r"\s+", " ", text)

    sentences = re.split(r"(?:\band\b|\bso\b|\bbut\b)", text)

    formatted = []
    for s in sentences:
        s = s.strip()
        if len(s) < 15:
            continue
        s = s.capitalize()
        if not s.endswith((".", "!", "?")):
            s += "."
        formatted.append(s)

    return " ".join(formatted)


def split_paragraphs(text: str) -> List[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    paragraphs = []
    buffer = []

    for s in sentences:
        buffer.append(s)
        if len(" ".join(buffer).split()) > 70:
            paragraphs.append(" ".join(buffer))
            buffer = []

    if buffer:
        paragraphs.append(" ".join(buffer))

    return paragraphs
