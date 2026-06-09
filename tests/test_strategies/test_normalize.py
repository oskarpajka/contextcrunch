from contextcrunch.strategies.normalize import NormalizeStrategy


class TestNormalize:
    def test_nfkc_normalization(self):
        s = NormalizeStrategy()
        result, changes = s.apply("\ufb01nd")
        assert result == "find"

    def test_already_normalized(self):
        s = NormalizeStrategy()
        result, changes = s.apply("hello world")
        assert result == "hello world"
        assert len(changes) == 0
