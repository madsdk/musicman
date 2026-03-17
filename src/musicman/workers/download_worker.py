"""QRunnable for background YouTube audio download."""

from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from musicman.models.track import Track
from musicman.services.downloader import download_video_audio, download_playlist_audio
from musicman.services.scanner import read_track


class DownloadSignals(QObject):
    finished = Signal(list)
    error = Signal(str)


class DownloadWorker(QRunnable):
    def __init__(self, id_value: str, output_dir: Path, is_playlist: bool = False):
        super().__init__()
        self.id_value = id_value
        self.output_dir = output_dir
        self.is_playlist = is_playlist
        self.signals = DownloadSignals()

    @Slot()
    def run(self):
        try:
            if self.is_playlist:
                filepaths = download_playlist_audio(self.id_value, self.output_dir)
            else:
                filepaths = [download_video_audio(self.id_value, self.output_dir)]

            tracks = []
            for filepath in filepaths:
                track = read_track(filepath)
                if track is None:
                    self.signals.error.emit(f"Could not read metadata from {filepath}")
                    return
                track.artist = "<Downloads>"
                tracks.append(track)

            self.signals.finished.emit(tracks)
        except Exception as e:
            self.signals.error.emit(str(e))
