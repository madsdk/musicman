"""Settings dialog for application preferences."""

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from musicman.services.settings import Settings


class SettingsDialog(QDialog):
    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self._settings = settings
        self.setWindowTitle("Settings")
        self.setMinimumWidth(450)

        layout = QVBoxLayout(self)

        form = QFormLayout()
        layout.addLayout(form)

        # Library root
        root_layout = QHBoxLayout()
        self._root_edit = QLineEdit(settings.library_root)
        root_layout.addWidget(self._root_edit)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_root)
        root_layout.addWidget(browse_btn)
        form.addRow("Library root:", root_layout)

        # Download folder
        dl_layout = QHBoxLayout()
        self._dl_edit = QLineEdit(settings.download_folder)
        dl_layout.addWidget(self._dl_edit)
        dl_browse_btn = QPushButton("Browse...")
        dl_browse_btn.clicked.connect(self._browse_download)
        dl_layout.addWidget(dl_browse_btn)
        form.addRow("Download folder:", dl_layout)

        # Transcode mode
        self._mode_combo = QComboBox()
        self._mode_combo.addItems(["CBR", "VBR"])
        self._mode_combo.setCurrentText(settings.transcode_mode.upper())
        self._mode_combo.currentTextChanged.connect(self._on_mode_changed)
        form.addRow("Transcode mode:", self._mode_combo)

        # CBR bitrate
        self._cbr_combo = QComboBox()
        for rate in [128, 192, 256, 320]:
            self._cbr_combo.addItem(f"{rate} kbps", rate)
        idx = self._cbr_combo.findData(settings.cbr_bitrate)
        if idx >= 0:
            self._cbr_combo.setCurrentIndex(idx)
        form.addRow("CBR bitrate:", self._cbr_combo)

        # VBR quality
        self._vbr_spin = QSpinBox()
        self._vbr_spin.setRange(0, 9)
        self._vbr_spin.setValue(settings.vbr_quality)
        self._vbr_label = QLabel("(0=best, 9=worst)")
        vbr_layout = QHBoxLayout()
        vbr_layout.addWidget(self._vbr_spin)
        vbr_layout.addWidget(self._vbr_label)
        form.addRow("VBR quality:", vbr_layout)

        self._on_mode_changed(self._mode_combo.currentText())

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _browse_root(self):
        path = QFileDialog.getExistingDirectory(self, "Select Library Root")
        if path:
            self._root_edit.setText(path)

    def _browse_download(self):
        path = QFileDialog.getExistingDirectory(self, "Select Download Folder")
        if path:
            self._dl_edit.setText(path)

    def _on_mode_changed(self, text):
        is_cbr = text.upper() == "CBR"
        self._cbr_combo.setEnabled(is_cbr)
        self._vbr_spin.setEnabled(not is_cbr)

    def _save(self):
        self._settings.library_root = self._root_edit.text()
        self._settings.download_folder = self._dl_edit.text()
        self._settings.transcode_mode = self._mode_combo.currentText().lower()
        self._settings.cbr_bitrate = self._cbr_combo.currentData()
        self._settings.vbr_quality = self._vbr_spin.value()
        self.accept()
