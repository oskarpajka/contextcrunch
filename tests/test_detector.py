from contextcrunch.detector import detect
from contextcrunch.types import ProtectedSpan


class TestDetector:
    def test_detects_double_quoted_strings(self):
        spans = detect('Say "hello world" please')
        quoted = [s for s in spans if s.kind == "double_quoted"]
        assert len(quoted) >= 1
        assert quoted[0].text == '"hello world"'

    def test_detects_single_quoted_strings(self):
        spans = detect("Use 'calculate_sum' as the name")
        quoted = [s for s in spans if s.kind == "single_quoted"]
        assert len(quoted) >= 1

    def test_detects_inline_code(self):
        spans = detect("Call `my_function()` to process")
        code = [s for s in spans if s.kind == "inline_code"]
        assert len(code) >= 1

    def test_detects_code_block(self):
        text = "Here:\n```python\nprint('hi')\n```\nDone"
        spans = detect(text)
        blocks = [s for s in spans if s.kind == "code_block"]
        assert len(blocks) >= 1

    def test_detects_urls(self):
        spans = detect("Visit https://example.com for info")
        urls = [s for s in spans if s.kind == "url"]
        assert len(urls) >= 1

    def test_detects_html_tags(self):
        spans = detect("Create a <div> and a </span> element")
        tags = [s for s in spans if s.kind == "html_tag"]
        assert len(tags) >= 2

    def test_detects_numbers(self):
        spans = detect("Set the value to 42")
        nums = [s for s in spans if s.kind == "number"]
        assert any(n.text == "42" for n in nums)

    def test_detects_hex_colors(self):
        spans = detect("Use color #FF0000 for red")
        colors = [s for s in spans if s.kind == "hex_color"]
        assert len(colors) >= 1

    def test_detects_email(self):
        spans = detect("Send to user@example.com please")
        emails = [s for s in spans if s.kind == "email"]
        assert len(emails) >= 1

    def test_detects_uuid(self):
        spans = detect("ID is 550e8400-e29b-41d4-a716-446655440000")
        uuids = [s for s in spans if s.kind == "uuid"]
        assert len(uuids) >= 1

    def test_no_overlaps(self):
        text = """Create a "quoted string" and visit https://example.com"""
        spans = detect(text)
        for i in range(len(spans)):
            for j in range(i + 1, len(spans)):
                assert spans[i].end <= spans[j].start or spans[j].end <= spans[i].start

    def test_custom_patterns(self):
        import re
        spans = detect("Use {{variable}} in template", extra_patterns=[re.compile(r"\{\{[^}]+\}\}")])
        custom = [s for s in spans if s.kind.startswith("custom_")]
        assert len(custom) >= 1
