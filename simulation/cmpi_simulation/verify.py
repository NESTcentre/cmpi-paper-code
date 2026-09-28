"""Sentence tokenisation and placement verification.

Position-indexing rule: slot 1 covers either the title (if present) or the first body sentence.
Slot 2 is the second body sentence; slot 3 is the third body sentence; and so on.
"""

import re
from typing import Optional

import nltk

# Ensure punkt is available for sentence tokenisation.
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("punkt_tab", quiet=True)


def split_sentences(body: str) -> list[str]:
    """Split a body string into sentences using NLTK's Punkt tokenizer."""
    return nltk.sent_tokenize(body.strip())


def _first_index_in(text: str, name: str) -> Optional[int]:
    """Return character offset of first exact-string occurrence of `name` in `text`, else None.

    Matching is whitespace-tolerant on internal spaces (one or more whitespace chars between tokens),
    so the LLM's variable spacing does not break detection.
    """
    if not text or not name:
        return None
    pattern = r"\s+".join(re.escape(tok) for tok in name.split())
    match = re.search(pattern, text)
    return match.start() if match else None


def first_occurrence_slot(*, title: Optional[str], body: str, name: str) -> Optional[int]:
    """Return the slot index where `name` first appears, or None if absent.

    Slot 1: title (if present) or first body sentence.
    Slot k (k>=2): the k-th body sentence.
    """
    if title and _first_index_in(title, name) is not None:
        return 1
    sentences = split_sentences(body)
    for i, sent in enumerate(sentences, start=1):
        if _first_index_in(sent, name) is not None:
            return 1 if i == 1 else i
    return None


def verify_placement(*, title: Optional[str], body: str, name: str, expected: str) -> tuple[bool, str]:
    """Verify that `name`'s first-occurrence slot matches `expected` ("slot1"/"slot2"/"slot3"/"none").

    Returns (ok, reason). reason is empty when ok=True.
    """
    slot = first_occurrence_slot(title=title, body=body, name=name)
    if expected == "none":
        if slot is None:
            return True, ""
        return False, f"Expected no occurrence; found at slot {slot}."
    expected_int = {"slot1": 1, "slot2": 2, "slot3": 3}[expected]
    if slot is None:
        return False, f"Expected slot {expected_int}; entity is absent."
    if slot != expected_int:
        return False, f"Expected slot {expected_int}; first occurrence is at slot {slot}."
    return True, ""
