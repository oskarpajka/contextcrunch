from contextcrunch.normalizer import normalize, normalize_unicode, normalize_whitespace, normalize_for_matching


class TestNormalizer:
    def test_normalize_unicode(self):
        assert normalize_unicode("\ufb01") == "fi"

    def test_normalize_whitespace_multiple_spaces(self):
        assert normalize_whitespace("hello   world") == "hello world"

    def test_normalize_whitespace_crlf(self):
        assert normalize_whitespace("hello\r\nworld") == "hello\nworld"

    def test_normalize_whitespace_triple_newline(self):
        assert normalize_whitespace("hello\n\n\nworld") == "hello\n\nworld"

    def test_normalize_for_matching(self):
        result = normalize_for_matching("  Hello   World  ")
        assert result == "hello world"

    def test_normalize_preserves_content(self):
        text = "Create a function"
        assert normalize(text) == "Create a function"
