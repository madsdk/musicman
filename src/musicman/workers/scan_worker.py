"""QRunnable for background library scanning."""

from pathlib import Path

from PySide6.QtCore import QObject, QRunnable, Signal, Slot

from musicman.models.track import Track
from musicman.services.scanner import scan_directory


class ScanSignals(QObject):
    finished = Signal(list)  # list[Track]
    error = Signal(str)


class ScanWorker(QRunnable):
    def __init__(self, root: Path):
        super().__init__()
        self.root = root
        self.signals = ScanSignals()

    @Slot()
    def run(self):
        try:
            tracks = scan_directory(self.root)
            self.signals.finished.emit(tracks)
        except Exception as e:
            self.signals.error.emit(str(e))
