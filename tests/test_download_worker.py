"""Tests for the download worker."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from musicman.models.track import Track
from musicman.workers.download_worker import DownloadWorker


class TestDownloadWorker:
    @patch("musicman.workers.download_worker.read_track")
    @patch("musicman.workers.download_worker.download_video_audio")
    def test_successful_video_download(self, mock_dl, mock_read):
        fake_path = Path("/downloads/song.opus")
        mock_dl.return_value = fake_path
        mock_read.return_value = Track(
            path=fake_path,
            title="Test Song",
            artist="Original Artist",
            album="Test Album",
            duration=120.0,
            format="opus",
        )

        worker = DownloadWorker("test123", Path("/downloads"))
        worker.signals.finished = MagicMock()
        worker.signals.error = MagicMock()

        worker.run()

        worker.signals.finished.emit.assert_called_once()
        tracks = worker.signals.finished.emit.call_args[0][0]
        assert isinstance(tracks, list)
        assert len(tracks) == 1
        assert tracks[0].artist == "<Downloads>"
        assert tracks[0].title == "Test Song"
        worker.signals.error.emit.assert_not_called()

    @patch("musicman.workers.download_worker.read_track")
    @patch("musicman.workers.download_worker.download_video_audio")
    def test_download_error(self, mock_dl, mock_read):
        mock_dl.side_effect = Exception("Network error")

        worker = DownloadWorker("bad_id", Path("/downloads"))
        worker.signals.finished = MagicMock()
        worker.signals.error = MagicMock()

        worker.run()

        worker.signals.error.emit.assert_called_once_with("Network error")
        worker.signals.finished.emit.assert_not_called()

    @patch("musicman.workers.download_worker.read_track")
    @patch("musicman.workers.download_worker.download_video_audio")
    def test_read_track_returns_none(self, mock_dl, mock_read):
        mock_dl.return_value = Path("/downloads/bad.bin")
        mock_read.return_value = None

        worker = DownloadWorker("test123", Path("/downloads"))
        worker.signals.finished = MagicMock()
        worker.signals.error = MagicMock()

        worker.run()

        worker.signals.error.emit.assert_called_once()
        assert "Could not read metadata" in worker.signals.error.emit.call_args[0][0]
        worker.signals.finished.emit.assert_not_called()

    @patch("musicman.workers.download_worker.read_track")
    @patch("musicman.workers.download_worker.download_playlist_audio")
    def test_successful_playlist_download(self, mock_dl, mock_read):
        fake_path1 = Path("/downloads/song1.opus")
        fake_path2 = Path("/downloads/song2.opus")
        mock_dl.return_value = [fake_path1, fake_path2]
        mock_read.side_effect = [
            Track(path=fake_path1, title="Song 1", artist="A", album="B", duration=60.0, format="opus"),
            Track(path=fake_path2, title="Song 2", artist="A", album="B", duration=90.0, format="opus"),
        ]

        worker = DownloadWorker("PLtest123", Path("/downloads"), is_playlist=True)
        worker.signals.finished = MagicMock()
        worker.signals.error = MagicMock()

        worker.run()

        worker.signals.finished.emit.assert_called_once()
        tracks = worker.signals.finished.emit.call_args[0][0]
        assert len(tracks) == 2
        assert all(t.artist == "<Downloads>" for t in tracks)
        worker.signals.error.emit.assert_not_called()
