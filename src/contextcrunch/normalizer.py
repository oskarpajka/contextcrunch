from __future__ import annotations

import unicodedata
import re


def normalize_unicode(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def normalize_whitespace(text: str) -> str:
    result = re.sub(r"[ \t]+", " ", text)
    result = re.sub(r"\r\n", "\n", result)
    result = re.sub(r"\n{3,}", "\n\n", result)
    return result.strip()


def normalize_for_matching(text: str) -> str:
    result = normalize_unicode(text)
    result = normalize_whitespace(result)
    return result.lower()


def normalize_for_matching_preserve_positions(text: str) -> str:
    result = normalize_unicode(text)
    return result.lower()


def normalize(text: str) -> str:
    result = normalize_unicode(text)
    result = normalize_whitespace(result)
    return result
