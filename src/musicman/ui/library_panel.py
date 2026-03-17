"""Library panel: Artist > Album > Track tree view."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from musicman.models.library import LibraryModel, TRACK_ROLE
from musicman.models.track import Track


class LibraryPanel(QWidget):
    add_to_queue = Signal(list)  # list[Track]

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Music tree
        self._library_model = LibraryModel()
        self._music_view = QTreeView()
        self._music_view.setModel(self._library_model)
        self._music_view.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)
        self._apply_header_modes()
        self._music_view.doubleClicked.connect(self._on_double_click)
        layout.addWidget(self._music_view)

        # Add to Queue button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self._add_btn = QPushButton("Add to Queue >>")
        self._add_btn.clicked.connect(self._on_add_clicked)
        btn_layout.addWidget(self._add_btn)
        layout.addLayout(btn_layout)

    def _apply_header_modes(self):
        header = self._music_view.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, header.ResizeMode.Stretch)
        header.setSectionResizeMode(1, header.ResizeMode.ResizeToContents)

    def load_tracks(self, tracks: list[Track]):
        """Load tracks into the library model."""
        self._library_model.load_tracks(tracks)
        self._apply_header_modes()
        self._music_view.expandAll()

    def _on_add_clicked(self):
        """Add selected artist/album/track nodes to the queue."""
        indexes = self._music_view.selectionModel().selectedIndexes()
        tracks = []
        seen = set()
        for index in indexes:
            if index.column() != 0:
                continue
            for t in self._library_model.get_tracks_for_index(index):
                if t.path not in seen:
                    seen.add(t.path)
                    tracks.append(t)
        if tracks:
            self.add_to_queue.emit(tracks)

    def _on_double_click(self, index):
        """Double-click a track to add it to the queue."""
        item = self._library_model.itemFromIndex(index)
        if item is None:
            return
        track = item.data(TRACK_ROLE)
        if track:
            self.add_to_queue.emit([track])
