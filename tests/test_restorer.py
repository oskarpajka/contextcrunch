from contextcrunch.restorer import restore


class TestRestorer:
    def test_restore_simple(self):
        replacements = {"\x00CC0000\x00": "hello"}
        result = restore("Say \x00CC0000\x00 now", replacements)
        assert result == "Say hello now"

    def test_restore_empty(self):
        result = restore("No placeholders", {})
        assert result == "No placeholders"
