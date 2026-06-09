from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ProtectedSpan:
    start: int
    end: int
    kind: str
    text: str


@dataclass(frozen=True)
class Change:
    type: str
    original: str
    replacement: str
    span: tuple[int, int]


@dataclass
class CompressionResult:
    compressed: str
    original_tokens: int
    compressed_tokens: int
    savings_percent: float
    changes: list[Change] = field(default_factory=list)
    protected_spans: list[tuple[int, int]] = field(default_factory=list)


@dataclass(frozen=True)
class Segment:
    text: str
    start: int
    end: int
    is_protected: bool = False
