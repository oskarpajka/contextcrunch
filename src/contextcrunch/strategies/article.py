from __future__ import annotations

import re

from contextcrunch.strategies.base import BaseStrategy
from contextcrunch.types import Change

_PRESERVED_PATTERNS = [
    re.compile(r"^the\s+\w+\s+(?:is|are|was|were|has|have|had|will|would|can|could|should|shall|may|might|must|does|do|did)", re.IGNORECASE),
    re.compile(r"\b(?:the|a|an)\s+(?:first|second|third|last|next|previous|only|same|other|such)\b", re.IGNORECASE),
]

_ARTICLE_PATTERN = re.compile(r"\b(?:an?|the)\s+(?=[a-zA-Z])", re.IGNORECASE)


class ArticleRemovalStrategy(BaseStrategy):
    @property
    def name(self) -> str:
        return "article_removal"

    @property
    def tier(self) -> int:
        return 1

    def apply(self, text: str, normalized_text: str | None = None) -> tuple[str, list[Change]]:
        changes: list[Change] = []
        protected_zones: list[tuple[int, int]] = []
        for pat in _PRESERVED_PATTERNS:
            for m in pat.finditer(text):
                protected_zones.append((m.start(), m.end()))

        result_parts: list[str] = []
        offset = 0
        for match in _ARTICLE_PATTERN.finditer(text):
            start = match.start()
            end = match.end()
            if any(ps <= start < pe for ps, pe in protected_zones):
                continue
            before = text[offset:start]
            result_parts.append(before)
            changes.append(self._make_change(match.group(), "", start, end))
            offset = end
        result_parts.append(text[offset:])
        return "".join(result_parts), changes
