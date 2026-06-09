from contextcrunch.token_counter import get_tokenizer


class TestTokenCounter:
    def test_count_tokens(self):
        tok = get_tokenizer("cl100k_base")
        count = tok.count("Hello, world!")
        assert count > 0

    def test_count_empty_string(self):
        tok = get_tokenizer("cl100k_base")
        count = tok.count("")
        assert count == 0

    def test_tokenize_returns_list(self):
        tok = get_tokenizer("cl100k_base")
        tokens = tok.tokenize("Hello world")
        assert isinstance(tokens, list)
        assert len(tokens) > 0

    def test_cache_returns_same_instance(self):
        tok1 = get_tokenizer("cl100k_base")
        tok2 = get_tokenizer("cl100k_base")
        assert tok1 is tok2
