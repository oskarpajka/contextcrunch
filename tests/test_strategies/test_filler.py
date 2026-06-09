from contextcrunch.strategies.filler import FillerStrategy


class TestFiller:
    def test_removes_basically(self):
        s = FillerStrategy()
        result, changes = s.apply("basically create a function")
        assert "basically" not in result.lower()

    def test_removes_just(self):
        s = FillerStrategy()
        result, changes = s.apply("just return the value")
        assert "just" not in result.lower()
