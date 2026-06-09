from __future__ import annotations

import re

from contextcrunch.strategies.base import BaseStrategy
from contextcrunch.types import Change


_IMPERATIVE_PATTERNS = [
    (re.compile(r"\b(?:you\s+should|you\s+need\s+to|you\s+must|you\s+have\s+to|it\s+is\s+necessary\s+to)\s+", re.IGNORECASE), ""),
    (re.compile(r"\b(?:please\s+kindly|kindly\s+please)\s+", re.IGNORECASE), "please "),
    (re.compile(r"\b(?:it\s+should\s+be|it\s+needs\s+to\s+be)\s+(\w+ed)", re.IGNORECASE), r"\1"),
    (re.compile(r"\bmake\s+sure\s+to\s+", re.IGNORECASE), ""),
    (re.compile(r"\bbe\s+sure\s+to\s+", re.IGNORECASE), ""),
    (re.compile(r"\bgo\s+ahead\s+and\s+", re.IGNORECASE), ""),
]


class RestructuringStrategy(BaseStrategy):
    @property
    def name(self) -> str:
        return "restructuring"

    @property
    def tier(self) -> int:
        return 2

    def apply(self, text: str, normalized_text: str | None = None) -> tuple[str, list[Change]]:
        changes: list[Change] = []
        result = text
        for pattern, replacement in _IMPERATIVE_PATTERNS:
            new_result = pattern.sub(lambda m: self._replace(m, replacement, changes), result)
            if new_result != result:
                result = new_result
        return result, changes

    def _replace(self, match: re.Match[str], replacement: str, changes: list[Change]) -> str:
        original = match.group()
        if callable(replacement):
            expanded = replacement(match)
        else:
            expanded = match.expand(replacement) if "\\" in replacement else replacement
        changes.append(self._make_change(original, expanded, match.start(), match.end()))
        return expanded
