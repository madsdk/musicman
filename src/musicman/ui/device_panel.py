"""Device file browser panel."""

from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QMessageBox,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from musicman.models.device import DeviceModel


class DevicePanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = DeviceModel()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._table = QTableView()
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self._table.verticalHeader().setVisible(False)
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self._table)

        btn_layout = QHBoxLayout()
        self._delete_btn = QPushButton("Delete")
        self._delete_btn.clicked.connect(self._on_delete)
        btn_layout.addWidget(self._delete_btn)
        self._refresh_btn = QPushButton("Refresh")
        self._refresh_btn.clicked.connect(self.refresh)
        btn_layout.addWidget(self._refresh_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

    @property
    def model(self) -> DeviceModel:
        return self._model

    def set_device_path(self, path: str):
        self._model.set_path(path)

    def refresh(self):
        self._model.refresh()

    def _on_delete(self):
        indexes = self._table.selectionModel().selectedRows()
        if not indexes:
            return
        names = [self._model.files[i.row()].name for i in indexes]
        reply = QMessageBox.question(
            self,
            "Delete Files",
            f"Delete {len(names)} file(s) from device?\n\n" + "\n".join(names[:10]),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            rows = sorted(set(i.row() for i in indexes), reverse=True)
            for row in rows:
                self._model.delete_file(row)
