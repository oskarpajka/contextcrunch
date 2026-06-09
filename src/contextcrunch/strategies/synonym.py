from __future__ import annotations

import json
import re

from contextcrunch.config import data_path
from contextcrunch.strategies.base import BaseStrategy
from contextcrunch.types import Change


class SynonymStrategy(BaseStrategy):
    def __init__(self) -> None:
        path = data_path("synonyms.json")
        with open(path, encoding="utf-8") as f:
            self._mappings: dict[str, str] = json.load(f)
        words = sorted(self._mappings.keys(), key=len, reverse=True)
        self._pattern = re.compile(
            r"\b(" + "|".join(re.escape(w) for w in words) + r")\b",
            re.IGNORECASE,
        )

    @property
    def name(self) -> str:
        return "synonym"

    @property
    def tier(self) -> int:
        return 2

    def apply(self, text: str, normalized_text: str | None = None) -> tuple[str, list[Change]]:
        changes: list[Change] = []
        result = self._pattern.sub(lambda m: self._replace(m, changes), text)
        return result, changes

    def _replace(self, match: re.Match[str], changes: list[Change]) -> str:
        original = match.group()
        key = original.lower()
        replacement = self._mappings.get(key, original)
        if replacement == original:
            return original
        if original[0].isupper() and replacement:
            replacement = replacement[0].upper() + replacement[1:]
        changes.append(self._make_change(original, replacement, match.start(), match.end()))
        return replacement
