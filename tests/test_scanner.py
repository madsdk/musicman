"""Tests for the music file scanner."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from musicman.services.scanner import read_track, scan_directory


class TestReadTrack:
    @patch("musicman.services.scanner.mutagen.File")
    def test_reads_metadata(self, mock_file):
        mock_audio = MagicMock()
        mock_audio.get.side_effect = lambda k: {
            "title": ["Test Song"],
            "artist": ["Test Artist"],
            "album": ["Test Album"],
        }.get(k)
        mock_audio.info.length = 180.5
        mock_file.return_value = mock_audio

        track = read_track(Path("/music/test.mp3"))
        assert track is not None
        assert track.title == "Test Song"
        assert track.artist == "Test Artist"
        assert track.album == "Test Album"
        assert track.duration == 180.5
        assert track.format == "mp3"

    @patch("musicman.services.scanner.mutagen.File")
    def test_handles_missing_tags(self, mock_file):
        mock_audio = MagicMock()
        mock_audio.get.return_value = None
        mock_audio.info.length = 60.0
        mock_file.return_value = mock_audio

        track = read_track(Path("/music/mysong.flac"))
        assert track.title == "mysong"
        assert track.artist == "Unknown Artist"
        assert track.album == "Unknown Album"

    @patch("musicman.services.scanner.mutagen.File")
    def test_handles_exception(self, mock_file):
        mock_file.side_effect = Exception("corrupt file")
        track = read_track(Path("/music/bad.mp3"))
        assert track is not None
        assert track.format == "mp3"


class TestScanDirectory:
    def test_scans_supported_files(self, tmp_path):
        (tmp_path / "song.mp3").write_bytes(b"fake")
        (tmp_path / "song.flac").write_bytes(b"fake")
        (tmp_path / "readme.txt").write_bytes(b"text")
        sub = tmp_path / "sub"
        sub.mkdir()
        (sub / "deep.ogg").write_bytes(b"fake")

        with patch("musicman.services.scanner.read_track") as mock_read:
            mock_read.return_value = MagicMock()
            tracks = scan_directory(tmp_path)
            # Should find mp3, flac, ogg but not txt
            assert mock_read.call_count == 3

    def test_empty_directory(self, tmp_path):
        tracks = scan_directory(tmp_path)
        assert tracks == []

    def test_nonexistent_directory(self):
        tracks = scan_directory(Path("/nonexistent/path"))
        assert tracks == []
