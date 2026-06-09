from __future__ import annotations

import json
import re

from contextcrunch.config import data_path
from contextcrunch.strategies.base import BaseStrategy
from contextcrunch.types import Change


class FillerStrategy(BaseStrategy):
    def __init__(self) -> None:
        path = data_path("filler_words.json")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self._words: set[str] = {w.lower() for w in data.get("filler_words", [])}
        self._phrases: list[str] = sorted(
            data.get("filler_phrases", []), key=len, reverse=True
        )
        self._phrase_pattern = re.compile(
            r"\s*(" + "|".join(re.escape(p) for p in self._phrases) + r")\s*",
            re.IGNORECASE,
        )
        self._word_pattern = re.compile(
            r"\s*\b(" + "|".join(re.escape(w) for w in sorted(self._words, key=len, reverse=True)) + r")\b\s*",
            re.IGNORECASE,
        )

    @property
    def name(self) -> str:
        return "filler"

    @property
    def tier(self) -> int:
        return 1

    def apply(self, text: str) -> tuple[str, list[Change]]:
        changes: list[Change] = []
        result = text

        matches = list(self._phrase_pattern.finditer(result))
        for match in reversed(matches):
            original = match.group()
            start, end = match.span()
            replacement = " " if start > 0 and end < len(result) else ""
            changes.append(self._make_change(original.strip(), "", start, end))
            result = result[:start] + replacement + result[end:]

        matches = list(self._word_pattern.finditer(result))
        for match in reversed(matches):
            original = match.group()
            start, end = match.span()
            replacement = " " if start > 0 and end < len(result) else ""
            changes.append(self._make_change(original.strip(), "", start, end))
            result = result[:start] + replacement + result[end:]

        return result, changes
