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
        self._mappings = {k: v for k, v in self._mappings.items() if v}
        phrases = sorted(self._mappings.keys(), key=len, reverse=True)
        self._pattern = re.compile(
            r"\b(" + "|".join(re.escape(p) for p in phrases) + r")\b",
            re.IGNORECASE,
        )

        empty_phrases = [k for k, v in json.load(open(path, encoding="utf-8")).items() if not v]
        empty_phrases_sorted = sorted(empty_phrases, key=len, reverse=True)
        self._empty_pattern = re.compile(
            r"(?:^|\s)\s*(" + "|".join(re.escape(p) for p in empty_phrases_sorted) + r")\s*(?=\w|[,.:;]|\s|$)",
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
        result = self._empty_pattern.sub(lambda m: self._replace_empty(m, changes), text)
        result = self._pattern.sub(lambda m: self._replace(m, changes), result)
        return result, changes

    def _replace_empty(self, match: re.Match[str], changes: list[Change]) -> str:
        original_full = match.group()
        leading = match.group()[:match.start(1) - match.start()]
        phrase = match.group(1)
        changes.append(self._make_change(original_full.strip(), "", match.start(), match.end()))
        return " " if leading else ""

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
