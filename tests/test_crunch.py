import pytest
from contextcrunch import crunch, compress, EmptyInputError


class TestCrunch:
    def test_basic_safe_compression(self):
        text = "Please create a function that basically just returns the sum of two numbers"
        result = crunch(text, level="safe")
        assert result.compressed
        assert result.original_tokens > 0
        assert result.compressed_tokens > 0
        assert result.savings_percent >= 0

    def test_empty_input_raises(self):
        with pytest.raises(EmptyInputError):
            crunch("")

    def test_whitespace_only_input_raises(self):
        with pytest.raises(EmptyInputError):
            crunch("   \n\t  ")

    def test_compressed_preserves_protected_content(self):
        text = "Please create a function called 'calculate_sum' that returns the total"
        result = crunch(text, level="safe")
        assert "calculate_sum" in result.compressed

    def test_url_preserved(self):
        text = "Please visit https://example.com/path for more info"
        result = crunch(text, level="safe")
        assert "https://example.com/path" in result.compressed

    def test_code_block_preserved(self):
        text = "Here is some code:\n```python\nprint('hello')\n```\nPlease review it"
        result = crunch(text, level="balanced")
        assert "print('hello')" in result.compressed

    def test_html_tags_preserved(self):
        text = "Create a <div> element with the text 'hello world'"
        result = crunch(text, level="safe")
        assert "<div>" in result.compressed

    def test_number_preserved(self):
        text = "Set the value to 42 and the ratio to 3.14"
        result = crunch(text, level="safe")
        assert "42" in result.compressed
        assert "3.14" in result.compressed

    def test_hex_color_preserved(self):
        text = "Make the background color #FF0000 and the text white"
        result = crunch(text, level="safe")
        assert "#FF0000" in result.compressed

    def test_balanced_more_aggressive_than_safe(self):
        text = "It is necessary to implement the functionality that utilizes the database"
        safe = crunch(text, level="safe")
        balanced = crunch(text, level="balanced")
        assert balanced.compressed_tokens <= safe.compressed_tokens

    def test_compress_returns_string(self):
        result = compress("Please create a function", level="safe")
        assert isinstance(result, str)

    def test_model_parameter(self):
        result = crunch("Please create a function", level="safe", model="gpt-4o")
        assert result.compressed

    def test_tokenizer_parameter(self):
        result = crunch("Please create a function", level="safe", tokenizer="cl100k_base")
        assert result.compressed

    def test_100_percent_protected(self):
        text = "https://example.com"
        result = crunch(text, level="safe")
        assert result.compressed == text
        assert result.savings_percent == 0.0

    def test_result_has_protected_spans(self):
        text = "Create a function called 'my_func' that works"
        result = crunch(text, level="safe")
        assert isinstance(result.protected_spans, list)

    def test_result_has_changes(self):
        text = "Please basically just create a function"
        result = crunch(text, level="safe")
        assert isinstance(result.changes, list)
