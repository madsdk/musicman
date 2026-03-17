"""Transfer progress dialog."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QLabel,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
)


class TransferProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Transferring...")
        self.setMinimumWidth(400)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)

        layout = QVBoxLayout(self)

        self._status_label = QLabel("Preparing...")
        layout.addWidget(self._status_label)

        self._progress = QProgressBar()
        self._progress.setRange(0, 100)
        layout.addWidget(self._progress)

        self._file_label = QLabel("")
        layout.addWidget(self._file_label)

        self._cancel_btn = QPushButton("Cancel")
        layout.addWidget(self._cancel_btn)

        self._cancelled = False
        self._cancel_callback = None

    def set_cancel_callback(self, callback):
        self._cancel_callback = callback
        self._cancel_btn.clicked.connect(self._on_cancel)

    def update_progress(self, current: int, total: int, filename: str):
        pct = int((current / total) * 100) if total > 0 else 0
        self._progress.setValue(pct)
        self._status_label.setText(f"Transferring {current + 1} of {total}...")
        self._file_label.setText(filename)

    def transfer_finished(self, errors: list[str]):
        if errors:
            self._status_label.setText(f"Completed with {len(errors)} error(s)")
            self._file_label.setText("\n".join(errors[:5]))
        else:
            self._status_label.setText("Transfer complete!")
            self._file_label.setText("")
        self._progress.setValue(100)
        self._cancel_btn.setText("Close")
        self._cancel_btn.clicked.disconnect()
        self._cancel_btn.clicked.connect(self.accept)

    def _on_cancel(self):
        self._cancelled = True
        self._status_label.setText("Cancelling...")
        self._cancel_btn.setEnabled(False)
        if self._cancel_callback:
            self._cancel_callback()
