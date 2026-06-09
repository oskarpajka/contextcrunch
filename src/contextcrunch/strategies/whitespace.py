from __future__ import annotations

import re

from contextcrunch.strategies.base import BaseStrategy
from contextcrunch.types import Change


class WhitespaceStrategy(BaseStrategy):
    @property
    def name(self) -> str:
        return "whitespace"

    @property
    def tier(self) -> int:
        return 1

    def apply(self, text: str, normalized_text: str | None = None) -> tuple[str, list[Change]]:
        changes: list[Change] = []
        result = re.sub(r" {2,}", " ", text)
        if result != text:
            changes.append(self._make_change(text, result, 0, len(text)))
        return result, changes
