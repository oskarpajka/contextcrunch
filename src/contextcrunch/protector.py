from __future__ import annotations

from contextcrunch.types import ProtectedSpan

PLACEHOLDER_PREFIX = "\x00CC"


def protect(text: str, spans: list[ProtectedSpan]) -> tuple[str, dict[str, str]]:
    if not spans:
        return text, {}
    replacements: dict[str, str] = {}
    parts: list[str] = []
    last_end = 0
    for i, span in enumerate(spans):
        parts.append(text[last_end:span.start])
        placeholder = f"{PLACEHOLDER_PREFIX}{i:04d}\x00"
        original_text = text[span.start:span.end]
        replacements[placeholder] = original_text
        parts.append(placeholder)
        last_end = span.end
    parts.append(text[last_end:])
    return "".join(parts), replacements


def restore(text: str, replacements: dict[str, str]) -> str:
    result = text
    for placeholder, original in replacements.items():
        result = result.replace(placeholder, original)
    return result
