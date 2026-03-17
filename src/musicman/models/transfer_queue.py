"""Ordered transfer queue model with drag-and-drop reordering and prefix generation."""

from PySide6.QtCore import QAbstractTableModel, QMimeData, QModelIndex, Qt

from musicman.models.track import Track


def generate_prefix(index: int) -> str:
    """Generate two-letter prefix AA–ZZ for position index (0-based)."""
    if index < 0 or index >= 676:
        return "??"
    return chr(65 + index // 26) + chr(65 + index % 26)


def sanitize_filename(name: str) -> str:
    """Sanitize a string for use in FAT32 filenames."""
    forbidden = '<>:"/\\|?*'
    result = "".join(c if c not in forbidden else "_" for c in name)
    # Collapse multiple underscores and strip
    while "__" in result:
        result = result.replace("__", "_")
    result = result.strip(". _")
    # Limit length (prefix + underscore takes 3 chars, .mp3 takes 4)
    max_len = 255 - 3 - 4
    return result[:max_len] if result else "track"


class TransferQueueModel(QAbstractTableModel):
    COLUMNS = ["#", "Prefix", "Title", "Artist"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._tracks: list[Track] = []

    @property
    def tracks(self) -> list[Track]:
        return list(self._tracks)

    def add_tracks(self, tracks: list[Track]):
        if not tracks:
            return
        pos = len(self._tracks)
        self.beginInsertRows(QModelIndex(), pos, pos + len(tracks) - 1)
        self._tracks.extend(tracks)
        self.endInsertRows()

    def remove_track(self, row: int):
        if 0 <= row < len(self._tracks):
            self.beginRemoveRows(QModelIndex(), row, row)
            self._tracks.pop(row)
            self.endRemoveRows()
            # Prefixes changed for all subsequent rows
            if row < len(self._tracks):
                self.dataChanged.emit(
                    self.index(row, 0),
                    self.index(len(self._tracks) - 1, len(self.COLUMNS) - 1),
                )

    def clear(self):
        self.beginResetModel()
        self._tracks.clear()
        self.endResetModel()

    def get_output_filename(self, row: int) -> str:
        if 0 <= row < len(self._tracks):
            prefix = generate_prefix(row)
            title = sanitize_filename(self._tracks[row].display_title)
            return f"{prefix}_{title}.mp3"
        return ""

    # --- Qt Model Interface ---

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._tracks)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.COLUMNS)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole:
            return None
        row = index.row()
        col = index.column()
        track = self._tracks[row]
        if col == 0:
            return row + 1
        if col == 1:
            return generate_prefix(row)
        if col == 2:
            return track.display_title
        if col == 3:
            return track.artist
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.COLUMNS[section]
        return None

    def flags(self, index):
        default = super().flags(index)
        if index.isValid():
            return default | Qt.ItemFlag.ItemIsDragEnabled
        return default | Qt.ItemFlag.ItemIsDropEnabled

    # --- Drag and Drop ---

    def supportedDropActions(self):
        return Qt.DropAction.MoveAction

    def mimeTypes(self):
        return ["application/x-musicman-queue-rows"]

    def mimeData(self, indexes):
        mime = QMimeData()
        rows = sorted(set(i.row() for i in indexes))
        mime.setData(
            "application/x-musicman-queue-rows",
            ",".join(str(r) for r in rows).encode(),
        )
        return mime

    def dropMimeData(self, data, action, row, column, parent):
        if action != Qt.DropAction.MoveAction:
            return False
        if not data.hasFormat("application/x-musicman-queue-rows"):
            return False

        source_rows = sorted(
            int(r)
            for r in data.data("application/x-musicman-queue-rows").data().decode().split(",")
        )

        # Determine insert position
        if row < 0:
            if parent.isValid():
                row = parent.row()
            else:
                row = len(self._tracks)

        # Extract tracks to move
        moved = [self._tracks[r] for r in source_rows]

        # Remove from end to start to preserve indices
        for r in reversed(source_rows):
            self.beginRemoveRows(QModelIndex(), r, r)
            self._tracks.pop(r)
            self.endRemoveRows()
            if r < row:
                row -= 1

        # Insert at target
        self.beginInsertRows(QModelIndex(), row, row + len(moved) - 1)
        for i, track in enumerate(moved):
            self._tracks.insert(row + i, track)
        self.endInsertRows()

        # All prefixes changed
        self.dataChanged.emit(
            self.index(0, 0),
            self.index(len(self._tracks) - 1, len(self.COLUMNS) - 1),
        )
        return True
