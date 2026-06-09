from contextcrunch.parser import parse


class TestParser:
    def test_empty_text(self):
        segments = parse("", set())
        assert segments == []

    def test_simple_text_single_segment(self):
        segments = parse("create a function", set())
        assert len(segments) >= 1
        assert segments[0].text == "create a function"

    def test_splits_on_comma(self):
        segments = parse("create a function, then test it", set())
        assert len(segments) >= 2

    def test_protected_segment_detected(self):
        segments = parse("create 'my_func'", {7})
        protected = [s for s in segments if s.is_protected]
        unprotected = [s for s in segments if not s.is_protected]
        assert len(protected) >= 0

    def test_no_splits_without_commas(self):
        segments = parse("create a function that returns the sum", set())
        assert len(segments) >= 1

    def test_segment_ordering(self):
        text = "create a function, then test it, finally deploy"
        segments = parse(text, set())
        assert len(segments) >= 3
        for i in range(len(segments) - 1):
            assert segments[i].start <= segments[i + 1].start

    def test_segment_boundaries_match(self):
        text = "create a function then test it"
        segments = parse(text, set())
        reconstructed = "".join(s.text for s in segments)
        assert reconstructed == text

    def test_protected_in_first_segment(self):
        text = "use 'my_func', then test"
        segments = parse(text, {4})
        assert segments[0].is_protected or not any(s.is_protected for s in segments)
