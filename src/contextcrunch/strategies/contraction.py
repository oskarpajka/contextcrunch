from __future__ import annotations

import json
import re

from contextcrunch.config import data_path
from contextcrunch.strategies.base import BaseStrategy
from contextcrunch.types import Change


class ContractionStrategy(BaseStrategy):
    def __init__(self) -> None:
        path = data_path("contractions.json")
        with open(path, encoding="utf-8") as f:
            self._expansions: dict[str, str] = json.load(f)
        self._contractions: dict[str, str] = {v.lower(): k for k, v in self._expansions.items()}
        phrases = sorted(self._contractions.keys(), key=len, reverse=True)
        self._pattern = re.compile(
            r"\b(" + "|".join(re.escape(p) for p in phrases) + r")\b",
            re.IGNORECASE,
        )

    @property
    def name(self) -> str:
        return "contraction"

    @property
    def tier(self) -> int:
        return 2

    def apply(self, text: str) -> tuple[str, list[Change]]:
        changes: list[Change] = []
        result = self._pattern.sub(lambda m: self._replace(m, changes), text)
        return result, changes

    def _replace(self, match: re.Match[str], changes: list[Change]) -> str:
        original = match.group()
        key = original.lower()
        contraction = self._contractions.get(key)
        if contraction is None:
            return original
        if original[0].isupper():
            contraction = contraction[0].upper() + contraction[1:]
        changes.append(self._make_change(original, contraction, match.start(), match.end()))
        return contraction
