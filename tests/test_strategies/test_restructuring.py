from contextcrunch.strategies.restructuring import RestructuringStrategy


class TestRestructuring:
    def test_you_should(self):
        s = RestructuringStrategy()
        result, changes = s.apply("You should create a function")
        assert "You should" not in result
        assert "create" in result

    def test_you_need_to(self):
        s = RestructuringStrategy()
        result, changes = s.apply("You need to implement this")
        assert "You need to" not in result
        assert "implement" in result
