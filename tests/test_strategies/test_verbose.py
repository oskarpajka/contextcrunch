from contextcrunch.strategies.verbose import VerboseStrategy


class TestVerbose:
    def test_in_order_to(self):
        s = VerboseStrategy()
        result, changes = s.apply("In order to create a function")
        assert "To create" in result
        assert "In order to" not in result

    def test_due_to_the_fact_that(self):
        s = VerboseStrategy()
        result, changes = s.apply("Due to the fact that it is late")
        assert "because" in result.lower()
