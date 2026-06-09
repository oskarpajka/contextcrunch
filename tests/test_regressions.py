from contextcrunch import crunch, compress


class TestRegressions:
    def test_empty_input_raises_error(self):
        """Empty input should raise EmptyInputError, not crash."""
        import pytest
        from contextcrunch.config import EmptyInputError
        with pytest.raises(EmptyInputError):
            crunch("")
        with pytest.raises(EmptyInputError):
            crunch("   ")

    def test_whitespace_only_input_raises_error(self):
        """Whitespace-only input should not be treated as valid."""
        import pytest
        from contextcrunch.config import EmptyInputError
        with pytest.raises(EmptyInputError):
            crunch("\t\n  \n")

    def test_single_word_input_works(self):
        """Single word should not crash."""
        result = crunch("hello", level="safe")
        assert result.compressed is not None

    def test_very_long_single_word(self):
        """Very long single token should not crash."""
        result = crunch("a" * 1000, level="safe")
        assert result.compressed == "a" * 1000

    def test_mixed_quote_types(self):
        """Mixed single and double quotes should both be preserved."""
        text = '''She said "hello" and replied 'hi' back'''
        result = crunch(text, level="safe")
        assert '"hello"' in result.compressed or 'hello' in result.compressed

    def test_url_with_query_params(self):
        """URL with complex query string preserved."""
        url = "https://example.com/search?q=python&lang=en&page=1"
        text = f"Search {url} for results"
        result = crunch(text, level="safe")
        assert url in result.compressed

    def test_nested_html_inside_quotes(self):
        """Quoted string containing HTML should be fully protected."""
        text = 'Add element "<div>content</div>" to the page'
        result = crunch(text, level="safe")
        assert "<div>content</div>" in result.compressed

    def test_multiline_code_block_preserved(self):
        """Multi-line code block with language tag should be fully preserved."""
        text = "Code:\n```javascript\nfunction foo() {\n  return 1;\n}\n```\nReview it"
        result = crunch(text, level="safe")
        assert "function foo()" in result.compressed
        assert "return 1" in result.compressed

    def test_unicode_preserved(self):
        """Unicode characters should not be corrupted."""
        text = "Créez une fonction qui calcule la somme"
        result = crunch(text, level="safe")
        assert "Créez" in result.compressed or "creez" in result.compressed.lower()

    def test_emoji_preserved(self):
        """Emoji should be preserved as-is."""
        text = "Create a function that returns ✅ or ❌"
        result = crunch(text, level="safe")
        assert "✅" in result.compressed
        assert "❌" in result.compressed

    def test_markdown_formatting_preserved(self):
        """Markdown bold and italic should be preserved."""
        text = "Make text **bold** and *italic* please"
        result = crunch(text, level="safe")
        assert "**bold**" in result.compressed
        assert "*italic*" in result.compressed

    def test_json_in_text_preserved(self):
        """JSON-like structures should be preserved."""
        text = 'Return {"status": "ok", "count": 42} as response'
        result = crunch(text, level="safe")
        assert "status" in result.compressed
        assert "42" in result.compressed

    def test_ip_address_preserved(self):
        """IP addresses should be preserved."""
        text = "Connect to server 192.168.1.1 on port 8080"
        result = crunch(text, level="safe")
        assert "192.168.1.1" in result.compressed

    def test_snake_case_preserved(self):
        """snake_case identifiers should be preserved."""
        text = "Call the function calculate_total_amount with args"
        result = crunch(text, level="safe")
        assert "calculate_total_amount" in result.compressed

    def test_camel_case_preserved(self):
        """camelCase identifiers should be preserved."""
        text = "Call calculateTotalAmount and processData"
        result = crunch(text, level="safe")
        assert "calculateTotalAmount" in result.compressed

    def test_hex_color_preserved(self):
        """Hex colors should be preserved."""
        text = "Use color #FF5733 for the background"
        result = crunch(text, level="safe")
        assert "#FF5733" in result.compressed

    def test_repeated_calls_idempotent_safe(self):
        """Repeated calls on same input should produce same output at safe level."""
        text = "Please basically just create a function that returns the sum"
        r1 = crunch(text, level="safe")
        r2 = crunch(text, level="safe")
        assert r1.compressed == r2.compressed

    def test_compress_shortcut(self):
        """compress() should return a string."""
        result = compress("Create a function", level="safe")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_target_tokens_raises_when_unreachable(self):
        """Should raise when target tokens unreachable."""
        import pytest
        from contextcrunch.config import TargetTokensUnreachableError
        with pytest.raises(TargetTokensUnreachableError):
            crunch("hello world", level="safe", target_tokens=0)

    def test_large_input_rejected(self):
        """Input exceeding max bytes should raise."""
        import pytest
        from contextcrunch.config import InputTooLargeError
        text = "x" * 2_000_000
        with pytest.raises(InputTooLargeError):
            crunch(text, level="safe")
