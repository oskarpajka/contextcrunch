from __future__ import annotations

from contextcrunch.config import (
    CompressionLevel,
    ContextCrunchError,
    EmptyInputError,
    InputTooLargeError,
    TargetTokensUnreachableError,
    Settings,
    resolve_tokenizer,
    SAFE_SAVINGS_THRESHOLD,
)
from contextcrunch.types import CompressionResult, Change, ProtectedSpan
from contextcrunch.detector import detect
from contextcrunch.protector import protect
from contextcrunch.restorer import restore
from contextcrunch.normalizer import normalize_for_matching_preserve_positions, normalize_whitespace
from contextcrunch.parser import parse
from contextcrunch.token_counter import get_tokenizer
from contextcrunch.strategies import get_strategies


def _run_pipeline(
    text: str,
    settings: Settings,
) -> CompressionResult:
    tok = get_tokenizer(settings.tokenizer_name)
    original_tokens = tok.count(text)

    protected = detect(text, settings.custom_protect_patterns)

    protected_text, replacements = protect(text, protected)

    matching_text = normalize_for_matching_preserve_positions(protected_text)

    placeholder_positions = {
        i for i, ch in enumerate(protected_text)
        if ch == "\x00" or (i < len(protected_text) - 1 and protected_text[i:i+2] == "\x00C")
    }
    segments = parse(protected_text, placeholder_positions)

    strategies = get_strategies(settings.level.value)

    working_text = protected_text
    all_changes: list[Change] = []

    for strategy in strategies:
        new_text, changes = strategy.apply(working_text, matching_text)
        if new_text != working_text:
            working_text = new_text
            matching_text = normalize_for_matching_preserve_positions(working_text)
            all_changes.extend(changes)

            if (
                settings.level == CompressionLevel.SAFE
                and strategy.tier == 1
            ):
                temp_result = restore(working_text, replacements)
                temp_tokens = tok.count(temp_result)
                if temp_tokens > 0:
                    savings = (1 - temp_tokens / original_tokens) * 100
                    if savings >= SAFE_SAVINGS_THRESHOLD:
                        break

    final_text = restore(working_text, replacements)
    final_text = normalize_whitespace(final_text)

    compressed_tokens = tok.count(final_text)

    savings_percent = (
        (1 - compressed_tokens / original_tokens) * 100
        if original_tokens > 0
        else 0.0
    )

    if settings.target_tokens is not None and compressed_tokens > settings.target_tokens:
        raise TargetTokensUnreachableError(
            f"Cannot compress to {settings.target_tokens} tokens; "
            f"best result is {compressed_tokens} tokens"
        )

    protected_spans = [(s.start, s.end) for s in protected]

    return CompressionResult(
        compressed=final_text,
        original_tokens=original_tokens,
        compressed_tokens=compressed_tokens,
        savings_percent=round(savings_percent, 1),
        changes=all_changes,
        protected_spans=protected_spans,
    )


def crunch(
    text: str,
    level: str = "safe",
    tokenizer: str | None = None,
    model: str | None = None,
    target_tokens: int | None = None,
    custom_protect_patterns: list | None = None,
    idempotent: bool = True,
) -> CompressionResult:
    if not text or not text.strip():
        raise EmptyInputError("Input text is empty or whitespace-only")

    settings = Settings(
        level=CompressionLevel(level),
        tokenizer_name=resolve_tokenizer(tokenizer, model),
        target_tokens=target_tokens,
        custom_protect_patterns=custom_protect_patterns or [],
        idempotent=idempotent,
    )

    if len(text.encode("utf-8")) > settings.max_input_bytes:
        raise InputTooLargeError(
            f"Input exceeds maximum size of {settings.max_input_bytes} bytes"
        )

    result = _run_pipeline(text, settings)

    if settings.idempotent and settings.level == CompressionLevel.SAFE:
        verify = _run_pipeline(result.compressed, settings)
        if verify.compressed != result.compressed:
            result = CompressionResult(
                compressed=verify.compressed,
                original_tokens=result.original_tokens,
                compressed_tokens=verify.compressed_tokens,
                savings_percent=round(
                    (1 - verify.compressed_tokens / result.original_tokens) * 100
                    if result.original_tokens > 0 else 0.0, 1
                ),
                changes=result.changes + verify.changes,
                protected_spans=result.protected_spans,
            )

    return result


def compress(
    text: str,
    level: str = "safe",
    tokenizer: str | None = None,
    model: str | None = None,
) -> str:
    result = crunch(text, level=level, tokenizer=tokenizer, model=model)
    return result.compressed
