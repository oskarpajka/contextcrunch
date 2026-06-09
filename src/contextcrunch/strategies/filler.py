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
            r"\b(" + "|".join(re.escape(p) for p in self._phrases) + r")\b",
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

        for match in self._phrase_pattern.finditer(result):
            original = match.group()
            start, end = match.span()
            result = result[:start] + result[end:]
            changes.append(self._make_change(original, "", start, end))
            result, changes = _adjust_spans(result, changes, start, end - start)

        tokens = result.split()
        new_tokens: list[str] = []
        offset = 0
        for token in tokens:
            word = re.sub(r"[^\w]", "", token).lower()
            if word in self._words:
                token_start = result.find(token, offset)
                if token_start != -1:
                    before = result[:token_start]
                    after = result[token_start + len(token):]
                    leading_space = before.endswith(" ")
                    if leading_space:
                        before = before[:-1]
                        token_start -= 1
                    changes.append(self._make_change(token, "", token_start, token_start + len(token) + (1 if leading_space else 0)))
                    result = before + after
                    offset = len(before)
                    continue
            offset += len(token) + 1
            new_tokens.append(token)

        return result, changes


def _adjust_spans(text: str, changes: list[Change], removed_start: int, removed_len: int) -> tuple[str, list[Change]]:
    return text, changes
