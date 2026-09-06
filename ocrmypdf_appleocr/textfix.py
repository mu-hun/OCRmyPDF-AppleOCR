"""Lightweight, conservative post-recognition text correction.

Applied to raw OCR output before it goes into the hOCR/PDF text layer. Only
touches two well-known Vision recognition quirks, and only when the fix is
safe to make unconditionally:

- a standalone lowercase "l" that should be the pronoun "I" (Vision
  occasionally reads the capital I glyph as a lowercase L in this font).
  Genuine standalone lowercase "l" essentially never occurs as an English
  word, so this conversion is unconditional. The literal pipe "|" is left
  alone: this document uses it as a real design glyph (day-number badges),
  not a misrecognition artifact.
- common contractions that lost their apostrophe (e.g. "Didnit" -> "Didn't",
  "cant" -> "can't"), checked against a fixed list of auxiliary/negation
  stems so it never touches an unrelated word that happens to end the same
  way.
"""

from __future__ import annotations

import re

# Stem -> full contraction, without the apostrophe, matched case-insensitively
# and re-cased to match the original token.
_AUX_STEMS = {
    "dont": "don't",
    "doesnt": "doesn't",
    "didnt": "didn't",
    "cant": "can't",
    "couldnt": "couldn't",
    "wont": "won't",
    "wouldnt": "wouldn't",
    "shouldnt": "shouldn't",
    "isnt": "isn't",
    "arent": "aren't",
    "wasnt": "wasn't",
    "werent": "weren't",
    "havent": "haven't",
    "hasnt": "hasn't",
    "hadnt": "hadn't",
    "im": "I'm",
    "ive": "I've",
    "ill": "I'll",
    "id": "I'd",
    "youre": "you're",
    "youve": "you've",
    "youll": "you'll",
    "theyre": "they're",
    "theyve": "they've",
    "were": None,  # ambiguous with the real word "were" -- never touch
    "wasn": None,
}

_TOKEN_RE = re.compile(r"[A-Za-z']+")


def _recase(fixed: str, original: str) -> str:
    if original.isupper():
        return fixed.upper()
    if original[0].isupper():
        return fixed[0].upper() + fixed[1:]
    return fixed


def _fix_token(tok: str) -> str:
    if tok == "l":
        return "I"
    bare = tok.replace("'", "").lower()
    repl = _AUX_STEMS.get(bare)
    if repl and "'" not in tok:
        return _recase(repl, tok)
    return tok


def fix_text(s: str) -> str:
    if not s:
        return s
    return _TOKEN_RE.sub(lambda m: _fix_token(m.group(0)), s)
