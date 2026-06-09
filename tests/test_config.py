from contextcrunch.config import CompressionLevel, resolve_tokenizer, ContextCrunchError, EmptyInputError


class TestConfig:
    def test_compression_level_values(self):
        assert CompressionLevel.SAFE.value == "safe"
        assert CompressionLevel.BALANCED.value == "balanced"
        assert CompressionLevel.AGGRESSIVE.value == "aggressive"

    def test_resolve_tokenizer_explicit(self):
        assert resolve_tokenizer(tokenizer="o200k_base") == "o200k_base"

    def test_resolve_tokenizer_from_model(self):
        assert resolve_tokenizer(model="gpt-4o") == "o200k_base"
        assert resolve_tokenizer(model="gpt-4") == "cl100k_base"

    def test_resolve_tokenizer_default(self):
        assert resolve_tokenizer() == "cl100k_base"

    def test_exception_hierarchy(self):
        assert issubclass(EmptyInputError, ContextCrunchError)
