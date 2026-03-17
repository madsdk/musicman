"""QRunnable for background transfer with progress reporting."""

from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from musicman.models.track import Track
from musicman.services.transfer import transfer_tracks


class TransferSignals(QObject):
    progress = Signal(int, int, str)  # current, total, filename
    finished = Signal(list)  # list of error strings
    error = Signal(str)


class TransferWorker(QRunnable):
    def __init__(
        self,
        tracks: list[Track],
        device_path: Path,
        mode: str = "cbr",
        cbr_bitrate: int = 192,
        vbr_quality: int = 2,
    ):
        super().__init__()
        self.tracks = tracks
        self.device_path = device_path
        self.mode = mode
        self.cbr_bitrate = cbr_bitrate
        self.vbr_quality = vbr_quality
        self.signals = TransferSignals()
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    @Slot()
    def run(self):
        try:
            errors = transfer_tracks(
                self.tracks,
                self.device_path,
                mode=self.mode,
                cbr_bitrate=self.cbr_bitrate,
                vbr_quality=self.vbr_quality,
                progress_callback=self._on_progress,
                cancel_check=lambda: self._cancelled,
            )
            self.signals.finished.emit(errors)
        except Exception as e:
            self.signals.error.emit(str(e))

    def _on_progress(self, current, total, filename):
        self.signals.progress.emit(current, total, filename)
