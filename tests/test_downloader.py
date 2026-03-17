"""Tests for the YouTube audio downloader service."""

from pathlib import Path
from unittest.mock import patch

import pytest

from musicman.services.downloader import DownloadError, download_audio


class TestDownloadAudio:
    @patch("musicman.services.downloader.subprocess.run")
    def test_successful_download(self, mock_run, tmp_path):
        output_file = tmp_path / "Test Video.opus"
        output_file.write_bytes(b"fake audio")

        mock_run.return_value = type("Result", (), {
            "stdout": f"{output_file}\n",
            "stderr": "",
            "returncode": 0,
        })()

        result = download_audio("https://youtube.com/watch?v=test", tmp_path)
        assert result == output_file

        cmd = mock_run.call_args[0][0]
        assert cmd[0] == "yt-dlp"
        assert "--extract-audio" in cmd
        assert "--audio-format" in cmd
        assert "best" in cmd
        assert "--print" in cmd
        assert "after_move:filepath" in cmd
        assert "https://youtube.com/watch?v=test" in cmd

    @patch("musicman.services.downloader.subprocess.run")
    def test_yt_dlp_not_installed(self, mock_run, tmp_path):
        mock_run.side_effect = FileNotFoundError()
        with pytest.raises(DownloadError, match="yt-dlp is not installed"):
            download_audio("https://youtube.com/watch?v=test", tmp_path)

    @patch("musicman.services.downloader.subprocess.run")
    def test_yt_dlp_failure(self, mock_run, tmp_path):
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(
            1, "yt-dlp", stderr="Invalid URL"
        )
        with pytest.raises(DownloadError, match="yt-dlp failed"):
            download_audio("https://youtube.com/watch?v=bad", tmp_path)

    @patch("musicman.services.downloader.subprocess.run")
    def test_empty_stdout(self, mock_run, tmp_path):
        mock_run.return_value = type("Result", (), {
            "stdout": "",
            "stderr": "",
            "returncode": 0,
        })()
        with pytest.raises(DownloadError, match="did not report"):
            download_audio("https://youtube.com/watch?v=test", tmp_path)

    @patch("musicman.services.downloader.subprocess.run")
    def test_creates_output_dir(self, mock_run, tmp_path):
        out_dir = tmp_path / "new_subdir"
        output_file = out_dir / "video.opus"

        # Pre-create so the file exists check passes
        out_dir.mkdir()
        output_file.write_bytes(b"fake")

        mock_run.return_value = type("Result", (), {
            "stdout": f"{output_file}\n",
            "stderr": "",
            "returncode": 0,
        })()

        result = download_audio("https://youtube.com/watch?v=test", out_dir)
        assert result == output_file
