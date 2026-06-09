from __future__ import annotations

from abc import ABC, abstractmethod
from contextcrunch.types import Change


class BaseStrategy(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def tier(self) -> int: ...

    @abstractmethod
    def apply(self, text: str, normalized_text: str | None = None) -> tuple[str, list[Change]]: ...

    def _make_change(self, original: str, replacement: str, start: int, end: int) -> Change:
        return Change(type=self.name, original=original, replacement=replacement, span=(start, end))
