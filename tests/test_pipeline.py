import pytest
from contextcrunch.crunch import crunch


class TestPipeline:
    def test_full_pipeline_safe(self):
        result = crunch(
            "Please basically just create a function that returns the sum of two numbers",
            level="safe",
        )
        assert result.compressed
        assert "sum" in result.compressed
        assert "function" in result.compressed.lower()

    def test_full_pipeline_balanced(self):
        result = crunch(
            "It is necessary to implement the functionality",
            level="balanced",
        )
        assert result.compressed
        assert len(result.compressed) < len("It is necessary to implement the functionality")

    def test_pipeline_preserves_quoted_content(self):
        text = """Create a function called 'calculate_sum' that basically returns the total"""
        result = crunch(text, level="safe")
        assert "calculate_sum" in result.compressed

    def test_pipeline_preserves_code_block(self):
        text = "Review this:\n```python\ndef foo():\n    pass\n```\nPlease check it basically"
        result = crunch(text, level="safe")
        assert "def foo():" in result.compressed

    def test_pipeline_preserves_url(self):
        text = "Visit https://example.com basically for more info please"
        result = crunch(text, level="safe")
        assert "https://example.com" in result.compressed

    def test_pipeline_preserves_numbers(self):
        text = "Set the value to 42 and basically the ratio to 3.14"
        result = crunch(text, level="safe")
        assert "42" in result.compressed
        assert "3.14" in result.compressed

    def test_safe_level_is_conservative(self):
        text = "Create a function that adds two numbers"
        result = crunch(text, level="safe")
        assert result.savings_percent <= 50

    def test_result_structure(self):
        result = crunch("Please create a function", level="safe")
        assert hasattr(result, "compressed")
        assert hasattr(result, "original_tokens")
        assert hasattr(result, "compressed_tokens")
        assert hasattr(result, "savings_percent")
        assert hasattr(result, "changes")
        assert hasattr(result, "protected_spans")
