from __future__ import annotations

from contextcrunch.protector import restore
from contextcrunch.types import ProtectedSpan, Change


def rebuild(text: str, replacements: dict[str, str], changes: list[Change]) -> str:
    restored = restore(text, replacements)
    return restored
