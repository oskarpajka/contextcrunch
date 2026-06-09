from __future__ import annotations

import enum
import re
from dataclasses import dataclass, field
from pathlib import Path


class CompressionLevel(enum.Enum):
    SAFE = "safe"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"


class ContextCrunchError(Exception):
    pass


class EmptyInputError(ContextCrunchError):
    pass


class InputTooLargeError(ContextCrunchError):
    pass


class TargetTokensUnreachableError(ContextCrunchError):
    pass


_MODEL_TO_TOKENIZER: dict[str, str] = {
    "gpt-4o": "o200k_base",
    "gpt-4o-mini": "o200k_base",
    "gpt-4-turbo": "cl100k_base",
    "gpt-4": "cl100k_base",
    "gpt-3.5-turbo": "cl100k_base",
    "text-embedding-ada-002": "cl100k_base",
    "text-embedding-3-small": "cl100k_base",
    "text-embedding-3-large": "cl100k_base",
}

DEFAULT_TOKENIZER = "cl100k_base"
DEFAULT_MAX_INPUT_BYTES = 1_000_000
SAFE_SAVINGS_THRESHOLD = 30.0


@dataclass
class Settings:
    level: CompressionLevel = CompressionLevel.SAFE
    tokenizer_name: str = DEFAULT_TOKENIZER
    target_tokens: int | None = None
    custom_protect_patterns: list[re.Pattern[str]] = field(default_factory=list)
    idempotent: bool = True
    max_input_bytes: int = DEFAULT_MAX_INPUT_BYTES


def resolve_tokenizer(tokenizer: str | None = None, model: str | None = None) -> str:
    if tokenizer is not None:
        return tokenizer
    if model is not None:
        return _MODEL_TO_TOKENIZER.get(model, DEFAULT_TOKENIZER)
    return DEFAULT_TOKENIZER


_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "mappings"


def data_path(filename: str) -> Path:
    pkg_data = Path(__file__).resolve().parent / "data" / "mappings" / filename
    if pkg_data.exists():
        return pkg_data
    return _DATA_DIR / filename
