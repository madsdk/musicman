"""Tests for the YouTube audio downloader service."""

from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from musicman.services.downloader import DownloadError, download_video_audio, download_playlist_audio


def _fake_popen(files_to_create, returncode=0, stderr=""):
    """Create a mock Popen that creates files when instantiated."""
    def factory(*args, **kwargs):
        for f in files_to_create:
            f.write_bytes(b"fake audio")
        proc = MagicMock()
        proc.communicate.return_value = ("", stderr)
        proc.returncode = returncode
        return proc
    return factory


class TestDownloadVideoAudio:
    @patch("musicman.services.downloader.subprocess.Popen")
    def test_successful_download(self, mock_popen, tmp_path):
        output_file = tmp_path / "Test Video.opus"
        mock_popen.side_effect = _fake_popen([output_file])

        result = download_video_audio("test123", tmp_path)
        assert result == output_file

        cmd = mock_popen.call_args[0][0]
        assert cmd[0] == "yt-dlp"
        assert "--ignore-config" in cmd
        assert "--no-playlist" in cmd
        assert "--extract-audio" in cmd
        assert "https://www.youtube.com/watch?v=test123" in cmd

    @patch("musicman.services.downloader.subprocess.Popen")
    def test_yt_dlp_not_installed(self, mock_popen, tmp_path):
        mock_popen.side_effect = FileNotFoundError()
        with pytest.raises(DownloadError, match="yt-dlp is not installed"):
            download_video_audio("test123", tmp_path)

    @patch("musicman.services.downloader.subprocess.Popen")
    def test_yt_dlp_failure(self, mock_popen, tmp_path):
        mock_popen.side_effect = _fake_popen([], returncode=1, stderr="Invalid URL")
        with pytest.raises(DownloadError, match="yt-dlp failed"):
            download_video_audio("bad_id", tmp_path)

    @patch("musicman.services.downloader.subprocess.Popen")
    def test_no_output_file(self, mock_popen, tmp_path):
        mock_popen.side_effect = _fake_popen([])
        with pytest.raises(DownloadError, match="did not produce"):
            download_video_audio("test123", tmp_path)

    @patch("musicman.services.downloader.subprocess.Popen")
    def test_creates_output_dir(self, mock_popen, tmp_path):
        out_dir = tmp_path / "new_subdir"
        output_file = out_dir / "video.opus"
        mock_popen.side_effect = _fake_popen([output_file])

        result = download_video_audio("test123", out_dir)
        assert result == output_file

    @patch("musicman.services.downloader.subprocess.Popen")
    def test_process_callback(self, mock_popen, tmp_path):
        output_file = tmp_path / "Test.opus"
        mock_popen.side_effect = _fake_popen([output_file])

        callback = MagicMock()
        download_video_audio("test123", tmp_path, process_callback=callback)
        callback.assert_called_once()


class TestDownloadPlaylistAudio:
    @patch("musicman.services.downloader.subprocess.Popen")
    def test_successful_playlist_download(self, mock_popen, tmp_path):
        file1 = tmp_path / "Song One.opus"
        file2 = tmp_path / "Song Two.opus"
        mock_popen.side_effect = _fake_popen([file1, file2])

        result = download_playlist_audio("PLtest123", tmp_path)
        assert set(result) == {file1, file2}

        cmd = mock_popen.call_args[0][0]
        assert cmd[0] == "yt-dlp"
        assert "--ignore-config" in cmd
        assert "--no-playlist" not in cmd
        assert "https://www.youtube.com/playlist?list=PLtest123" in cmd

    @patch("musicman.services.downloader.subprocess.Popen")
    def test_no_output_files(self, mock_popen, tmp_path):
        mock_popen.side_effect = _fake_popen([])
        with pytest.raises(DownloadError, match="did not produce"):
            download_playlist_audio("PLtest123", tmp_path)

    @patch("musicman.services.downloader.subprocess.Popen")
    def test_yt_dlp_not_installed(self, mock_popen, tmp_path):
        mock_popen.side_effect = FileNotFoundError()
        with pytest.raises(DownloadError, match="yt-dlp is not installed"):
            download_playlist_audio("PLtest123", tmp_path)
