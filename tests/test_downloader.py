"""Tests for the YouTube audio downloader service."""

import threading
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from musicman.services.downloader import DownloadError, download_video_audio, download_playlist_audio


def _fake_ytdl(files_to_create, retcode=0, error=None):
    """Create a mock YoutubeDL context manager that creates files on download."""
    class FakeYDL:
        def __init__(self, opts):
            self.opts = opts

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def download(self, urls):
            if error:
                raise error
            # Call progress hooks if registered
            for hook in self.opts.get("progress_hooks", []):
                hook({
                    "status": "downloading",
                    "downloaded_bytes": 500,
                    "total_bytes": 1000,
                    "filename": "test.opus",
                })
            for f in files_to_create:
                f.write_bytes(b"fake audio")
            return retcode

    return FakeYDL


class TestDownloadVideoAudio:
    @patch("musicman.services.downloader.yt_dlp.YoutubeDL")
    def test_successful_download(self, mock_ydl_cls, tmp_path):
        output_file = tmp_path / "Test Video.opus"
        mock_ydl_cls.side_effect = _fake_ytdl([output_file])

        result = download_video_audio("test123", tmp_path)
        assert result == output_file

        opts = mock_ydl_cls.call_args[0][0]
        assert opts["noplaylist"] is True

    @patch("musicman.services.downloader.yt_dlp.YoutubeDL")
    def test_yt_dlp_failure(self, mock_ydl_cls, tmp_path):
        mock_ydl_cls.side_effect = _fake_ytdl([], retcode=1)
        with pytest.raises(DownloadError, match="non-zero exit code"):
            download_video_audio("bad_id", tmp_path)

    @patch("musicman.services.downloader.yt_dlp.YoutubeDL")
    def test_yt_dlp_exception(self, mock_ydl_cls, tmp_path):
        mock_ydl_cls.side_effect = _fake_ytdl([], error=RuntimeError("Invalid URL"))
        with pytest.raises(DownloadError, match="yt-dlp failed"):
            download_video_audio("bad_id", tmp_path)

    @patch("musicman.services.downloader.yt_dlp.YoutubeDL")
    def test_no_output_file(self, mock_ydl_cls, tmp_path):
        mock_ydl_cls.side_effect = _fake_ytdl([])
        with pytest.raises(DownloadError, match="did not produce"):
            download_video_audio("test123", tmp_path)

    @patch("musicman.services.downloader.yt_dlp.YoutubeDL")
    def test_creates_output_dir(self, mock_ydl_cls, tmp_path):
        out_dir = tmp_path / "new_subdir"
        output_file = out_dir / "video.opus"
        mock_ydl_cls.side_effect = _fake_ytdl([output_file])

        result = download_video_audio("test123", out_dir)
        assert result == output_file

    @patch("musicman.services.downloader.yt_dlp.YoutubeDL")
    def test_cancel_event(self, mock_ydl_cls, tmp_path):
        cancel = threading.Event()
        cancel.set()
        with pytest.raises(DownloadError, match="cancelled"):
            download_video_audio("test123", tmp_path, cancel_event=cancel)

    @patch("musicman.services.downloader.yt_dlp.YoutubeDL")
    def test_progress_callback_called(self, mock_ydl_cls, tmp_path):
        output_file = tmp_path / "Test Video.opus"
        mock_ydl_cls.side_effect = _fake_ytdl([output_file])
        cb = MagicMock()

        download_video_audio("test123", tmp_path, progress_callback=cb)

        cb.assert_called_once_with(50.0, "test.opus")


class TestDownloadPlaylistAudio:
    @patch("musicman.services.downloader.yt_dlp.YoutubeDL")
    def test_successful_playlist_download(self, mock_ydl_cls, tmp_path):
        file1 = tmp_path / "Song One.opus"
        file2 = tmp_path / "Song Two.opus"
        mock_ydl_cls.side_effect = _fake_ytdl([file1, file2])

        result = download_playlist_audio("PLtest123", tmp_path)
        assert set(result) == {file1, file2}

        opts = mock_ydl_cls.call_args[0][0]
        assert "noplaylist" not in opts

    @patch("musicman.services.downloader.yt_dlp.YoutubeDL")
    def test_no_output_files(self, mock_ydl_cls, tmp_path):
        mock_ydl_cls.side_effect = _fake_ytdl([])
        with pytest.raises(DownloadError, match="did not produce"):
            download_playlist_audio("PLtest123", tmp_path)

    @patch("musicman.services.downloader.yt_dlp.YoutubeDL")
    def test_yt_dlp_exception(self, mock_ydl_cls, tmp_path):
        mock_ydl_cls.side_effect = _fake_ytdl([], error=RuntimeError("bad"))
        with pytest.raises(DownloadError, match="yt-dlp failed"):
            download_playlist_audio("PLtest123", tmp_path)
