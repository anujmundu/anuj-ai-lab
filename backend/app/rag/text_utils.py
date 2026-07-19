from __future__ import annotations

import re


_SENTENCE_PATTERN = re.compile(r"(?<=[.!?])\s+")


def split_sentences(text: str) -> list[str]:
    """
    Split text into sentences.
    """

    if not text.strip():
        return []

    return [
        sentence.strip()
        for sentence in _SENTENCE_PATTERN.split(text.strip())
        if sentence.strip()
    ]