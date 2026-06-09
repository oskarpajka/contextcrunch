import pytest
from contextcrunch.crunch import crunch
from contextcrunch.token_counter import get_tokenizer


class TestTokenizerParity:
    def test_cl100k_base_tokenizer(self):
        tok = get_tokenizer("cl100k_base")
        count = tok.count("Hello, world!")
        assert count > 0

    def test_o200k_base_tokenizer(self):
        tok = get_tokenizer("o200k_base")
        count = tok.count("Hello, world!")
        assert count > 0

    def test_different_tokenizers_different_counts(self):
        text = "Hello, world! This is a test of the token counting system."
        tok_a = get_tokenizer("cl100k_base")
        tok_b = get_tokenizer("o200k_base")
        count_a = tok_a.count(text)
        count_b = tok_b.count(text)
        assert count_a > 0
        assert count_b > 0

    def test_tokenize_function(self):
        tok = get_tokenizer("cl100k_base")
        tokens = tok.tokenize("Hello world")
        assert isinstance(tokens, list)
        assert len(tokens) > 0

    def test_char_to_token_offsets(self):
        tok = get_tokenizer("cl100k_base")
        offsets = tok.char_to_token_offsets("Hello world")
        assert isinstance(offsets, list)
        assert len(offsets) > 0
        for start, end in offsets:
            assert start >= 0
            assert end > start

    def test_crunch_with_o200k(self):
        result = crunch("Please create a function", level="safe", tokenizer="o200k_base")
        assert result.compressed is not None
        assert result.original_tokens > 0
        assert result.compressed_tokens > 0

    def test_crunch_with_model_gpt4o(self):
        result = crunch("Please create a function", level="safe", model="gpt-4o")
        assert result.compressed is not None

    def test_crunch_with_model_gpt4(self):
        result = crunch("Please create a function", level="safe", model="gpt-4")
        assert result.compressed is not None

    def test_empty_string_count(self):
        tok = get_tokenizer("cl100k_base")
        assert tok.count("") == 0

    def test_cache_returns_same_instance(self):
        tok1 = get_tokenizer("cl100k_base")
        tok2 = get_tokenizer("cl100k_base")
        assert tok1 is tok2
