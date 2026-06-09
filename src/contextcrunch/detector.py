from __future__ import annotations

import re
from contextcrunch.types import ProtectedSpan

_REGEX_CACHE: list[tuple[str, re.Pattern[str]]] = []


def _build_regex_cache() -> None:
    if _REGEX_CACHE:
        return
    patterns: list[tuple[str, str, int]] = [
        ("code_block", r"```[\s\S]*?```", 0),
        ("inline_code", r"`[^`\n]+`", 0),
        ("double_quoted", r'"(?:[^"\\]|\\.)*"', 0),
        ("single_quoted", r"'(?:[^'\\]|\\.)*'", 0),
        ("html_tag", r"</?[a-zA-Z][a-zA-Z0-9]*(?:\s[^>]*)?/?>", 0),
        ("url", r"https?://[^\s<>\"]+|www\.[^\s<>\"]+", 0),
        ("email", r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", 0),
        ("ipv4", r"\b(?:\d{1,3}\.){3}\d{1,3}\b", 0),
        ("ipv6", r"\b(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}\b", 0),
        ("hex_color", r"#[0-9a-fA-F]{3,8}\b", 0),
        ("uuid", r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\b", 0),
        ("version", r"\bv?\d+\.\d+(?:\.\d+)?(?:-[a-zA-Z0-9]+)?\b", 0),
        ("git_hash", r"\b[0-9a-f]{7,40}\b", 0),
        ("iso_date", r"\b\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?)?\b", 0),
        ("base64", r"\b[A-Za-z0-9+/]{40,}={0,2}\b", 0),
        ("regex_pattern", r"(?:^|(?<=\s))/[^/\n]+/[gimsuxy]*", 0),
        ("sql_query", r"\b(?:SELECT|INSERT|UPDATE|DELETE|CREATE\s+(?:TABLE|INDEX|VIEW)|ALTER\s+(?:TABLE|INDEX|VIEW)|DROP\s+(?:TABLE|INDEX|VIEW))\b[\s\S]*?;", 0),
        ("latex", r"\$[^$]+\$|\$\$[\s\S]*?\$\$", 0),
        ("json_object", r"\{[^}]*(?:\{[^}]*\}[^}]*)*\}", 0),
        ("file_path", r"(?:^|(?<=\s))(?:[a-zA-Z]:[/\\]|~?/)(?:[\w.-]+[/\\])*[\w.-]+", 0),
        ("snake_case", r"\b[a-z][a-zA-Z0-9]*_[a-z][a-zA-Z0-9]*(?:_[a-z][a-zA-Z0-9]*)*\b", 0),
        ("camel_case", r"\b[a-z][a-z0-9]*(?:[A-Z][a-z0-9]*){2,}\b", 0),
        ("number", r"\b\d+(?:\.\d+)?(?:e[+-]?\d+)?\b", 0),
        ("emoji", r"[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U0000FE00-\U0000FE0F\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF\U00002600-\U000026FF](?:\u200D[^\u200D\s])*", 0),
        ("markdown_bold", r"\*\*[^*]+\*\*", 0),
        ("markdown_italic", r"\*[^*]+\*", 0),
        ("markdown_link", r"\[[^\]]+\]\([^)]+\)", 0),
        ("markdown_header", r"^#{1,6}\s+.+", re.MULTILINE),
        ("markdown_list", r"^(?:[*\-+]|\d+\.)\s+.+", re.MULTILINE),
        ("markdown_blockquote", r"^>\s?.+", re.MULTILINE),
        ("domain", r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(?:\/[^\s]*)?\b", 0),
        ("shell_command", r"\b(?:ls|cat|grep|find|rm|cp|mv|chmod|chown|echo|mkdir|touch|cd|pwd|ps|kill|sudo|apt|yum|pip|npm|yarn|docker|kubectl|curl|wget|ssh|scp|git|make|cmake|gcc|python|node|ruby|bash|sh|zsh)\s+(?:-[a-zA-Z0-9]+(?:\s+[^\s]+)*|\S+)", 0),
        ("yaml_key_value", r"^(?:[ \t]*[a-zA-Z_][a-zA-Z0-9_]*\s*:\s*.+)$", re.MULTILINE),
        ("markdown_table", r"^\|.+\|\s*$(?:\n^\|[-:| ]+\|\s*$(?:\n^\|.+\|\s*$)*)?", re.MULTILINE),
        ("csv_row", '(?:^|(?<=\n))\\s*(?:"[^"]*"|[^,\\s"][^,"]{0,30})(?:,\\s*(?:"[^"]*"|[^,\\s"][^,"]{0,30})){2,}\\s*(?:\n|$)', 0),
    ]
    for kind, pat, flags in patterns:
        _REGEX_CACHE.append((kind, re.compile(pat, flags)))


_SPECIFICITY: dict[str, int] = {
    "code_block": 10,
    "inline_code": 9,
    "json_object": 8,
    "double_quoted": 7,
    "single_quoted": 7,
    "html_tag": 6,
    "url": 5,
    "domain": 5,
    "email": 4,
    "file_path": 4,
    "regex_pattern": 4,
    "sql_query": 3,
    "shell_command": 3,
    "latex": 3,
    "yaml_key_value": 3,
    "markdown_table": 3,
    "csv_row": 3,
    "markdown_header": 2,
    "markdown_blockquote": 2,
    "markdown_list": 2,
    "snake_case": 2,
    "camel_case": 2,
    "markdown_bold": 2,
    "markdown_italic": 2,
    "markdown_link": 2,
    "ipv6": 2,
    "ipv4": 2,
    "number": 1,
}

_ADJACENT_MERGE_GAP = 2


def detect(text: str, extra_patterns: list[re.Pattern[str]] | None = None) -> list[ProtectedSpan]:
    _build_regex_cache()
    spans: list[ProtectedSpan] = []

    for kind, pattern in _REGEX_CACHE:
        for m in pattern.finditer(text):
            spans.append(ProtectedSpan(start=m.start(), end=m.end(), kind=kind, text=m.group()))

    if extra_patterns:
        for i, pattern in enumerate(extra_patterns):
            for m in pattern.finditer(text):
                spans.append(ProtectedSpan(start=m.start(), end=m.end(), kind=f"custom_{i}", text=m.group()))

    spans = _resolve_overlaps(spans)
    spans = _merge_adjacent(spans, _ADJACENT_MERGE_GAP)
    return spans


def _resolve_overlaps(spans: list[ProtectedSpan]) -> list[ProtectedSpan]:
    if not spans:
        return []
    spans.sort(key=lambda s: (s.start, -s.end))
    result: list[ProtectedSpan] = []
    for span in spans:
        if not result:
            result.append(span)
            continue
        last = result[-1]
        if span.start >= last.end:
            result.append(span)
            continue
        if span.start >= last.start and span.end <= last.end:
            continue
        if span.start < last.start or span.end > last.end:
            new_len = span.end - span.start
            last_len = last.end - last.start
            if new_len > last_len:
                result.pop()
                result.append(span)
            elif new_len == last_len:
                span_spec = _SPECIFICITY.get(span.kind, 0)
                last_spec = _SPECIFICITY.get(last.kind, 0)
                if span_spec > last_spec:
                    result.pop()
                    result.append(span)
    return result


def _merge_adjacent(spans: list[ProtectedSpan], gap: int) -> list[ProtectedSpan]:
    if len(spans) <= 1:
        return spans
    spans.sort(key=lambda s: s.start)
    result: list[ProtectedSpan] = [spans[0]]
    for span in spans[1:]:
        last = result[-1]
        if span.kind == last.kind and span.start - last.end <= gap:
            merged = ProtectedSpan(
                start=last.start,
                end=span.end,
                kind=last.kind,
                text="",
            )
            result[-1] = merged
        else:
            result.append(span)
    return result
