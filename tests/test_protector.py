from contextcrunch.protector import protect, restore
from contextcrunch.types import ProtectedSpan


class TestProtector:
    def test_protect_and_restore(self):
        text = 'Say "hello" please'
        spans = [ProtectedSpan(start=4, end=11, kind="double_quoted", text='"hello"')]
        protected, replacements = protect(text, spans)
        assert '"hello"' not in protected
        restored = restore(protected, replacements)
        assert restored == text

    def test_protect_no_spans(self):
        text = "No protected content here"
        protected, replacements = protect(text, [])
        assert protected == text
        assert replacements == {}

    def test_protect_multiple_spans(self):
        text = 'Use "foo" and "bar" please'
        spans = [
            ProtectedSpan(start=4, end=9, kind="double_quoted", text='"foo"'),
            ProtectedSpan(start=14, end=19, kind="double_quoted", text='"bar"'),
        ]
        protected, replacements = protect(text, spans)
        assert '"foo"' not in protected
        assert '"bar"' not in protected
        restored = restore(protected, replacements)
        assert restored == text

    def test_restore_after_modification(self):
        text = 'Say "hello" please'
        spans = [ProtectedSpan(start=4, end=11, kind="double_quoted", text='"hello"')]
        protected, replacements = protect(text, spans)
        modified = protected.replace("please", "")
        restored = restore(modified, replacements)
        assert '"hello"' in restored
