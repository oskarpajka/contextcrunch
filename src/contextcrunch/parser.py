from __future__ import annotations

import re

from contextcrunch.types import Segment


def parse(text: str, protected_start_positions: set[int]) -> list[Segment]:
    if not text:
        return []

    spans = _find_comma_clauses(text)
    if not spans:
        spans = [(0, len(text))]

    segments: list[Segment] = []
    for start, end in spans:
        seg_text = text[start:end]
        is_protected = any(
            start <= ps < end or start <= ps + len(text) - 1 < end
            for ps in protected_start_positions
        )
        segments.append(Segment(text=seg_text, start=start, end=end, is_protected=is_protected))

    return segments


def _find_comma_clauses(text: str) -> list[tuple[int, int]]:
    parts = re.split(r"(,\s+)", text)
    spans: list[tuple[int, int]] = []
    offset = 0
    for i, part in enumerate(parts):
        if i % 2 == 0:
            if part.strip():
                spans.append((offset, offset + len(part)))
        offset += len(part)

    if not spans:
        spans = [(0, len(text))]

    return spans
