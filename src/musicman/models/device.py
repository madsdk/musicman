"""Model for device file listing."""

from pathlib import Path

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt


class DeviceModel(QAbstractTableModel):
    COLUMNS = ["Filename", "Size"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._path: Path | None = None
        self.files: list[Path] = []

    def set_path(self, path: str):
        self.beginResetModel()
        self._path = Path(path) if path else None
        self._scan()
        self.endResetModel()

    def refresh(self):
        self.beginResetModel()
        self._scan()
        self.endResetModel()

    def _scan(self):
        self.files = []
        if self._path and self._path.is_dir():
            self.files = sorted(
                [f for f in self._path.iterdir() if f.is_file()],
                key=lambda f: f.name.lower(),
            )

    def delete_file(self, row: int):
        if 0 <= row < len(self.files):
            path = self.files[row]
            try:
                path.unlink()
                self.beginRemoveRows(QModelIndex(), row, row)
                self.files.pop(row)
                self.endRemoveRows()
            except OSError:
                pass

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.files)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.COLUMNS)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        f = self.files[index.row()]
        if index.column() == 0:
            return f.name
        if index.column() == 1:
            return _format_size(f.stat().st_size)
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.COLUMNS[section]
        return None


def _format_size(size: int) -> str:
    if size >= 1024 * 1024:
        return f"{size / (1024 * 1024):.1f} MB"
    if size >= 1024:
        return f"{size / 1024:.0f} KB"
    return f"{size} B"
