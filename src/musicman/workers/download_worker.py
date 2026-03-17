"""QRunnable for background YouTube audio download."""

from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from musicman.models.track import Track
from musicman.services.downloader import download_audio
from musicman.services.scanner import read_track


class DownloadSignals(QObject):
    finished = Signal(Track)
    error = Signal(str)


class DownloadWorker(QRunnable):
    def __init__(self, url: str, output_dir: Path):
        super().__init__()
        self.url = url
        self.output_dir = output_dir
        self.signals = DownloadSignals()

    @Slot()
    def run(self):
        try:
            filepath = download_audio(self.url, self.output_dir)
            track = read_track(filepath)
            if track is None:
                self.signals.error.emit(f"Could not read metadata from {filepath}")
                return
            track.artist = "<Downloads>"
            self.signals.finished.emit(track)
        except Exception as e:
            self.signals.error.emit(str(e))
