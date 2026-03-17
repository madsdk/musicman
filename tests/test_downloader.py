"""Tests for the YouTube audio downloader service."""

from pathlib import Path
from unittest.mock import patch

import pytest

from musicman.services.downloader import DownloadError, download_video_audio, download_playlist_audio


class TestDownloadVideoAudio:
    @patch("musicman.services.downloader.subprocess.run")
    def test_successful_download(self, mock_run, tmp_path):
        # Pre-create the output file so it appears as a "new" file
        output_file = tmp_path / "Test Video.opus"

        def fake_run(*args, **kwargs):
            output_file.write_bytes(b"fake audio")
            return type("Result", (), {"stdout": "", "stderr": "", "returncode": 0})()

        mock_run.side_effect = fake_run

        result = download_video_audio("test123", tmp_path)
        assert result == output_file

        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "yt-dlp"
        assert "--no-playlist" in cmd
        assert "--extract-audio" in cmd
        assert "--audio-format" in cmd
        assert "best" in cmd
        assert "https://www.youtube.com/watch?v=test123" in cmd

    @patch("musicman.services.downloader.subprocess.run")
    def test_yt_dlp_not_installed(self, mock_run, tmp_path):
        mock_run.side_effect = FileNotFoundError()
        with pytest.raises(DownloadError, match="yt-dlp is not installed"):
            download_video_audio("test123", tmp_path)

    @patch("musicman.services.downloader.subprocess.run")
    def test_yt_dlp_failure(self, mock_run, tmp_path):
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "yt-dlp", stderr="Invalid URL"
        )
        with pytest.raises(DownloadError, match="yt-dlp failed"):
            download_video_audio("bad_id", tmp_path)

    @patch("musicman.services.downloader.subprocess.run")
    def test_no_output_file(self, mock_run, tmp_path):
        mock_run.return_value = type("Result", (), {
            "stdout": "", "stderr": "", "returncode": 0,
        })()
        with pytest.raises(DownloadError, match="did not produce"):
            download_video_audio("test123", tmp_path)

    @patch("musicman.services.downloader.subprocess.run")
    def test_creates_output_dir(self, mock_run, tmp_path):
        out_dir = tmp_path / "new_subdir"
        output_file = out_dir / "video.opus"

        def fake_run(*args, **kwargs):
            output_file.write_bytes(b"fake")
            return type("Result", (), {"stdout": "", "stderr": "", "returncode": 0})()

        mock_run.side_effect = fake_run

        result = download_video_audio("test123", out_dir)
        assert result == output_file


class TestDownloadPlaylistAudio:
    @patch("musicman.services.downloader.subprocess.run")
    def test_successful_playlist_download(self, mock_run, tmp_path):
        file1 = tmp_path / "Song One.opus"
        file2 = tmp_path / "Song Two.opus"

        def fake_run(*args, **kwargs):
            file1.write_bytes(b"fake audio 1")
            file2.write_bytes(b"fake audio 2")
            return type("Result", (), {"stdout": "", "stderr": "", "returncode": 0})()

        mock_run.side_effect = fake_run

        result = download_playlist_audio("PLtest123", tmp_path)
        assert set(result) == {file1, file2}

        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "yt-dlp"
        assert "--no-playlist" not in cmd
        assert "https://www.youtube.com/playlist?list=PLtest123" in cmd

    @patch("musicman.services.downloader.subprocess.run")
    def test_no_output_files(self, mock_run, tmp_path):
        mock_run.return_value = type("Result", (), {
            "stdout": "", "stderr": "", "returncode": 0,
        })()
        with pytest.raises(DownloadError, match="did not produce"):
            download_playlist_audio("PLtest123", tmp_path)

    @patch("musicman.services.downloader.subprocess.run")
    def test_yt_dlp_not_installed(self, mock_run, tmp_path):
        mock_run.side_effect = FileNotFoundError()
        with pytest.raises(DownloadError, match="yt-dlp is not installed"):
            download_playlist_audio("PLtest123", tmp_path)
