"""Tests for prefix generation and filename sanitization."""

from musicman.models.transfer_queue import generate_prefix, sanitize_filename


class TestGeneratePrefix:
    def test_first(self):
        assert generate_prefix(0) == "AA"

    def test_second(self):
        assert generate_prefix(1) == "AB"

    def test_26th(self):
        assert generate_prefix(25) == "AZ"

    def test_27th(self):
        assert generate_prefix(26) == "BA"

    def test_last(self):
        assert generate_prefix(675) == "ZZ"

    def test_out_of_range(self):
        assert generate_prefix(676) == "??"
        assert generate_prefix(-1) == "??"


class TestSanitizeFilename:
    def test_basic(self):
        assert sanitize_filename("Hello World") == "Hello World"

    def test_forbidden_chars(self):
        result = sanitize_filename('track<1>:"test"')
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert '"' not in result

    def test_dots_stripped(self):
        result = sanitize_filename("...test...")
        assert result == "test"

    def test_empty_becomes_track(self):
        assert sanitize_filename("") == "track"
        assert sanitize_filename("???") == "track"

    def test_length_limit(self):
        long = "a" * 300
        result = sanitize_filename(long)
        assert len(result) <= 248  # 255 - 3 (prefix+_) - 4 (.mp3)
