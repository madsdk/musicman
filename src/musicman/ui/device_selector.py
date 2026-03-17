"""Device selector bar with combo box, path entry, and browse button."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QWidget,
)

from musicman.services.device_detect import detect_removable_volumes


class DeviceSelector(QWidget):
    device_changed = Signal(str)  # path

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        layout.addWidget(QLabel("Device:"))

        self._combo = QComboBox()
        self._combo.setMinimumWidth(150)
        self._combo.currentTextChanged.connect(self._on_combo_changed)
        layout.addWidget(self._combo)

        self._path_edit = QLineEdit()
        self._path_edit.setPlaceholderText("/path/to/device")
        self._path_edit.returnPressed.connect(self._on_path_entered)
        layout.addWidget(self._path_edit, stretch=1)

        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self._on_browse)
        layout.addWidget(browse_btn)

        refresh_btn = QPushButton("\u21bb")
        refresh_btn.setToolTip("Refresh devices")
        refresh_btn.setFixedWidth(30)
        refresh_btn.clicked.connect(self.refresh_devices)
        layout.addWidget(refresh_btn)

        self._free_label = QLabel()
        layout.addWidget(self._free_label)

    def refresh_devices(self):
        self._combo.blockSignals(True)
        current = self._combo.currentText()
        self._combo.clear()
        volumes = detect_removable_volumes()
        for label, path in volumes:
            self._combo.addItem(label, path)
        # Restore previous selection if still present
        idx = self._combo.findText(current)
        if idx >= 0:
            self._combo.setCurrentIndex(idx)
        self._combo.blockSignals(False)

    def set_path(self, path: str):
        self._path_edit.setText(path)
        self._update_free_space(path)
        self.device_changed.emit(path)

    def current_path(self) -> str:
        return self._path_edit.text()

    def _on_combo_changed(self, _text):
        path = self._combo.currentData()
        if path:
            self._path_edit.setText(path)
            self._update_free_space(path)
            self.device_changed.emit(path)

    def _on_path_entered(self):
        path = self._path_edit.text()
        self._update_free_space(path)
        self.device_changed.emit(path)

    def _on_browse(self):
        path = QFileDialog.getExistingDirectory(self, "Select Device Path")
        if path:
            self._path_edit.setText(path)
            self._update_free_space(path)
            self.device_changed.emit(path)

    def _update_free_space(self, path: str):
        try:
            import shutil
            usage = shutil.disk_usage(path)
            free_mb = usage.free / (1024 * 1024)
            if free_mb > 1024:
                self._free_label.setText(f"Free: {free_mb / 1024:.1f} GB")
            else:
                self._free_label.setText(f"Free: {free_mb:.0f} MB")
        except Exception:
            self._free_label.setText("")
