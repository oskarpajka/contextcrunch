from __future__ import annotations

import unicodedata

from contextcrunch.strategies.base import BaseStrategy
from contextcrunch.types import Change


class NormalizeStrategy(BaseStrategy):
    @property
    def name(self) -> str:
        return "normalize"

    @property
    def tier(self) -> int:
        return 1

    def apply(self, text: str) -> tuple[str, list[Change]]:
        changes: list[Change] = []
        normalized = unicodedata.normalize("NFKC", text)
        if normalized != text:
            changes.append(self._make_change(text, normalized, 0, len(text)))
        return normalized, changes
