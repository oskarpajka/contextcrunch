from contextcrunch.strategies.whitespace import WhitespaceStrategy


class TestWhitespace:
    def test_collapses_multiple_spaces(self):
        s = WhitespaceStrategy()
        result, changes = s.apply("hello   world")
        assert result == "hello world"

    def test_no_change_single_spaces(self):
        s = WhitespaceStrategy()
        result, changes = s.apply("hello world")
        assert result == "hello world"
        assert len(changes) == 0
