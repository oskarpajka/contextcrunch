from contextcrunch.strategies.abbreviation import AbbreviationStrategy


class TestAbbreviation:
    def test_abbreviates_please(self):
        s = AbbreviationStrategy()
        result, changes = s.apply("please create a function")
        assert "please" not in result.lower()

    def test_abbreviates_function(self):
        s = AbbreviationStrategy()
        result, changes = s.apply("create a function")
        assert "function" not in result.lower() or "fn" in result.lower()

    def test_abbreviates_variable(self):
        s = AbbreviationStrategy()
        result, changes = s.apply("declare a variable")
        assert "variable" not in result.lower() or "var" in result.lower()

    def test_removes_context_clutter(self):
        s = AbbreviationStrategy()
        result, changes = s.apply("As an AI assistant, create a function")
        assert "As an AI assistant" not in result

    def test_removes_you_are_an_expert(self):
        s = AbbreviationStrategy()
        result, changes = s.apply("You are an expert Python developer. Create a function")
        assert "You are an expert" not in result

    def test_removes_let_me_know(self):
        s = AbbreviationStrategy()
        result, changes = s.apply("Create a function. Let me know if you need anything else")
        assert "Let me know if you need anything else" not in result

    def test_preserves_normal_text_when_no_abbrevs(self):
        s = AbbreviationStrategy()
        result, changes = s.apply("Create a function that adds two numbers")
        assert "function" not in result.lower() or "fn" in result.lower()

    def test_idempotent_application(self):
        s = AbbreviationStrategy()
        text = "As an expert, please create a function that implements the database configuration"
        r1, _ = s.apply(text)
        r2, _ = s.apply(r1)
        assert r1 == r2
