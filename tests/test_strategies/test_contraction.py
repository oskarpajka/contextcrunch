from contextcrunch.strategies.contraction import ContractionStrategy


class TestContraction:
    def test_do_not_contraction(self):
        s = ContractionStrategy()
        result, changes = s.apply("do not create the function")
        assert "don't" in result

    def test_it_is_contraction(self):
        s = ContractionStrategy()
        result, changes = s.apply("it is necessary")
        assert "it's" in result
