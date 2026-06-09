from contextcrunch.strategies.synonym import SynonymStrategy


class TestSynonym:
    def test_utilize_to_use(self):
        s = SynonymStrategy()
        result, changes = s.apply("utilize the database")
        assert "use" in result.lower()

    def test_approximately_to_about(self):
        s = SynonymStrategy()
        result, changes = s.apply("approximately 100 items")
        assert "about" in result.lower()
