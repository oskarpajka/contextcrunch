from __future__ import annotations

import json
import re

from contextcrunch.config import data_path
from contextcrunch.strategies.base import BaseStrategy
from contextcrunch.types import Change


class VerboseStrategy(BaseStrategy):
    def __init__(self) -> None:
        path = data_path("verbose_phrases.json")
        with open(path, encoding="utf-8") as f:
            self._mappings: dict[str, str] = json.load(f)
        phrases = sorted(self._mappings.keys(), key=len, reverse=True)
        self._pattern = re.compile(
            r"\b(" + "|".join(re.escape(p) for p in phrases) + r")\b",
            re.IGNORECASE,
        )

    @property
    def name(self) -> str:
        return "verbose"

    @property
    def tier(self) -> int:
        return 1

    def apply(self, text: str) -> tuple[str, list[Change]]:
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
        if not replacement:
            before = match.string[:match.start()]
            if before.endswith(" "):
                changes.append(self._make_change(" " + original, "", match.start() - 1, match.end()))
            else:
                changes.append(self._make_change(original, "", match.start(), match.end()))
        else:
            changes.append(self._make_change(original, replacement, match.start(), match.end()))
        return replacement
