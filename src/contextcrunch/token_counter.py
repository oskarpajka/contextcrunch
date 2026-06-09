from __future__ import annotations

import tiktoken
from typing import Protocol


class Tokenizer(Protocol):
    def count(self, text: str) -> int: ...
    def tokenize(self, text: str) -> list[str]: ...
    def char_to_token_offsets(self, text: str) -> list[tuple[int, int]]: ...


class TiktokenTokenizer:
    def __init__(self, encoding_name: str = "cl100k_base") -> None:
        self._encoding = tiktoken.get_encoding(encoding_name)

    def count(self, text: str) -> int:
        return len(self._encoding.encode(text))

    def tokenize(self, text: str) -> list[str]:
        tokens = self._encoding.encode(text)
        return [self._encoding.decode([t]) for t in tokens]

    def char_to_token_offsets(self, text: str) -> list[tuple[int, int]]:
        result: list[tuple[int, int]] = []
        tokens = self._encoding.encode(text)
        byte_offset = 0
        for token in tokens:
            token_bytes = self._encoding.decode([token])
            char_len = len(token_bytes)
            result.append((byte_offset, byte_offset + char_len))
            byte_offset += char_len
        return result


_tokenizer_cache: dict[str, TiktokenTokenizer] = {}


def get_tokenizer(encoding_name: str = "cl100k_base") -> TiktokenTokenizer:
    if encoding_name not in _tokenizer_cache:
        _tokenizer_cache[encoding_name] = TiktokenTokenizer(encoding_name)
    return _tokenizer_cache[encoding_name]
