import pytest

pytest.importorskip("hypothesis", reason="hypothesis not installed")

import re
from hypothesis import given, strategies as st
from contextcrunch.crunch import crunch

_CRUFT = st.sampled_from([
    "please", "basically", "just", "really", "actually",
    "simply", "very", "quite", "literally",
])


@given(st.text(alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ ",
               min_size=1, max_size=100).filter(lambda t: t.strip()))
def test_never_raises_on_plain_text(text):
    result = crunch(text, level="safe")
    assert result.compressed is not None
    assert result.original_tokens > 0


@given(st.lists(
    st.sampled_from([
        '"hello world"', "'calc_sum'", "`my_func()`",
        "https://x.com/p", "<div>", "#FF0", "42",
        "user@x.com", "**bold**", "snake_var", "camelVar",
    ]), min_size=1, max_size=3))
def test_protected_content_never_mutated(protected_items):
    text = "Create " + " ".join(protected_items) + " now"
    result = crunch(text, level="safe")
    for item in protected_items:
        assert item in result.compressed


@given(st.lists(_CRUFT, min_size=1, max_size=3))
def test_filler_removed_in_safe(cruft_items):
    text = " ".join(cruft_items) + " create a function"
    result = crunch(text, level="safe")
    for item in cruft_items:
        assert item not in result.compressed.lower()


@given(st.text(alphabet="abcxyz ", min_size=1, max_size=50).filter(lambda t: t.strip()))
def test_safe_never_increases_tokens(text):
    result = crunch(text, level="safe")
    assert result.compressed_tokens <= result.original_tokens


@given(st.sampled_from(["safe", "balanced", "aggressive"]))
def test_all_levels_return_result(level):
    text = "Create a function that returns the sum"
    result = crunch(text, level=level)
    assert result.compressed is not None
    assert result.compressed_tokens <= result.original_tokens


def test_pipeline_preserves_urls():
    urls = [
        "https://example.com/path?query=1&foo=bar",
        "http://www.example.org",
    ]
    for url in urls:
        text = f"Visit {url} for info"
        result = crunch(text, level="safe")
        assert url in result.compressed


def test_pipeline_preserves_quoted_strings():
    texts = [
        ('Say "hello world" please', '"hello world"'),
        ("Use 'calculate_sum' as name", "'calculate_sum'"),
    ]
    for text, expected in texts:
        result = crunch(text, level="safe")
        assert expected in result.compressed


def test_pipeline_preserves_code_blocks():
    text = "Review:\n```python\nprint('hello')\n```\nThanks"
    result = crunch(text, level="safe")
    assert "print('hello')" in result.compressed


def test_pipeline_preserves_html_tags():
    text = "Create a <div class='container'> element"
    result = crunch(text, level="safe")
    assert "<div" in result.compressed


def test_pipeline_preserves_numbers():
    text = "Set count to 42 and ratio to 3.14159"
    result = crunch(text, level="safe")
    assert "42" in result.compressed
    assert "3.14159" in result.compressed


def test_pipeline_preserves_hex_colors():
    text = "Make background #FF0000 and text #00FF00"
    result = crunch(text, level="safe")
    assert "#FF0000" in result.compressed
    assert "#00FF00" in result.compressed


def test_pipeline_preserves_emails():
    text = "Send report to user@example.com for review"
    result = crunch(text, level="safe")
    assert "user@example.com" in result.compressed


def test_pipeline_preserves_uuids():
    uuid = "550e8400-e29b-41d4-a716-446655440000"
    text = f"Process ID {uuid} immediately"
    result = crunch(text, level="safe")
    assert uuid in result.compressed


def test_pipeline_preserves_version_strings():
    text = "Upgrade to version v2.3.1 for new features"
    result = crunch(text, level="safe")
    assert "2.3.1" in result.compressed


def test_pipeline_preserves_file_paths():
    text = "Read from /home/user/data/file.txt and process"
    result = crunch(text, level="safe")
    assert "/home/user/data/file.txt" in result.compressed


def test_100_percent_protected_unchanged():
    text = "https://example.com"
    result = crunch(text, level="safe")
    assert result.compressed == text
    assert result.savings_percent == 0.0


def test_balanced_more_compression_than_safe():
    text = "It is necessary to implement the functionality that utilizes the database in order to process requests"
    safe = crunch(text, level="safe")
    balanced = crunch(text, level="balanced")
    assert balanced.compressed_tokens <= safe.compressed_tokens


def test_aggressive_more_compression_than_balanced():
    text = "As an expert Python developer, implement a function that utilizes the configuration module"
    balanced = crunch(text, level="balanced")
    aggressive = crunch(text, level="aggressive")
    assert aggressive.compressed_tokens <= balanced.compressed_tokens


def test_result_includes_metadata():
    result = crunch("Create a function", level="safe")
    assert hasattr(result, "compressed")
    assert hasattr(result, "original_tokens")
    assert hasattr(result, "compressed_tokens")
    assert hasattr(result, "savings_percent")
    assert hasattr(result, "changes")
    assert hasattr(result, "protected_spans")
