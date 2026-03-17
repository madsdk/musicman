"""Tests for the Track dataclass."""

from pathlib import Path

from musicman.models.track import Track


class TestTrack:
    def test_duration_str(self):
        t = Track(path=Path("/x.mp3"), duration=185.7)
        assert t.duration_str == "3:05"

    def test_duration_str_zero(self):
        t = Track(path=Path("/x.mp3"), duration=0)
        assert t.duration_str == "0:00"

    def test_display_title_with_title(self):
        t = Track(path=Path("/music/file.mp3"), title="My Song")
        assert t.display_title == "My Song"

    def test_display_title_fallback(self):
        t = Track(path=Path("/music/my_track.mp3"))
        assert t.display_title == "my_track"
