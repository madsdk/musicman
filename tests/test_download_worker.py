"""Tests for the download worker."""

from pathlib import Path
from unittest.mock import MagicMock, patch

from musicman.models.track import Track
from musicman.workers.download_worker import DownloadWorker


class TestDownloadWorker:
    @patch("musicman.workers.download_worker.read_track")
    @patch("musicman.workers.download_worker.download_audio")
    def test_successful_download(self, mock_dl, mock_read):
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

        worker = DownloadWorker("https://youtube.com/watch?v=test", Path("/downloads"))
        worker.signals.finished = MagicMock()
        worker.signals.error = MagicMock()

        worker.run()

        worker.signals.finished.emit.assert_called_once()
        track = worker.signals.finished.emit.call_args[0][0]
        assert track.artist == "<Downloads>"
        assert track.title == "Test Song"
        worker.signals.error.emit.assert_not_called()

    @patch("musicman.workers.download_worker.read_track")
    @patch("musicman.workers.download_worker.download_audio")
    def test_download_error(self, mock_dl, mock_read):
        mock_dl.side_effect = Exception("Network error")

        worker = DownloadWorker("https://youtube.com/watch?v=bad", Path("/downloads"))
        worker.signals.finished = MagicMock()
        worker.signals.error = MagicMock()

        worker.run()

        worker.signals.error.emit.assert_called_once_with("Network error")
        worker.signals.finished.emit.assert_not_called()

    @patch("musicman.workers.download_worker.read_track")
    @patch("musicman.workers.download_worker.download_audio")
    def test_read_track_returns_none(self, mock_dl, mock_read):
        mock_dl.return_value = Path("/downloads/bad.bin")
        mock_read.return_value = None

        worker = DownloadWorker("https://youtube.com/watch?v=test", Path("/downloads"))
        worker.signals.finished = MagicMock()
        worker.signals.error = MagicMock()

        worker.run()

        worker.signals.error.emit.assert_called_once()
        assert "Could not read metadata" in worker.signals.error.emit.call_args[0][0]
        worker.signals.finished.emit.assert_not_called()
