"""Library panel: folder tree + music tree with Artist > Album > Track."""

from pathlib import Path

from PySide6.QtCore import QDir, QSortFilterProxyModel, Qt, Signal
from PySide6.QtWidgets import (
    QFileSystemModel,
    QHBoxLayout,
    QPushButton,
    QSplitter,
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
        self._all_tracks: list[Track] = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Horizontal splitter: folder tree | music tree
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(self._splitter)

        # Folder tree
        self._folder_model = QFileSystemModel()
        self._folder_model.setFilter(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot)
        self._folder_view = QTreeView()
        self._folder_view.setModel(self._folder_model)
        self._folder_view.setHeaderHidden(True)
        # Hide Size, Type, Date columns
        for col in range(1, self._folder_model.columnCount()):
            self._folder_view.hideColumn(col)
        self._splitter.addWidget(self._folder_view)

        # Music tree
        self._library_model = LibraryModel()
        self._music_view = QTreeView()
        self._music_view.setModel(self._library_model)
        self._music_view.setSelectionMode(QTreeView.SelectionMode.ExtendedSelection)
        self._music_view.header().setStretchLastSection(False)
        self._music_view.header().setSectionResizeMode(
            0, self._music_view.header().ResizeMode.Stretch
        )
        self._music_view.doubleClicked.connect(self._on_double_click)
        self._splitter.addWidget(self._music_view)

        self._splitter.setSizes([200, 400])

        # Add to Queue button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self._add_btn = QPushButton("Add to Queue >>")
        self._add_btn.clicked.connect(self._on_add_clicked)
        btn_layout.addWidget(self._add_btn)
        layout.addLayout(btn_layout)

        # Folder selection filters music tree
        self._folder_view.selectionModel().currentChanged.connect(
            self._on_folder_selected
        )

    def set_library_root(self, root: str):
        """Set the root path for the folder tree."""
        if not root:
            return
        root_index = self._folder_model.setRootPath(root)
        self._folder_view.setRootIndex(root_index)

    def load_tracks(self, tracks: list[Track]):
        """Load tracks into the library model."""
        self._all_tracks = tracks
        self._library_model.load_tracks(tracks)
        self._music_view.expandAll()

    def _on_folder_selected(self, current, _previous):
        """Filter the music tree to show only tracks under the selected folder."""
        path = self._folder_model.filePath(current)
        if not path:
            self._library_model.load_tracks(self._all_tracks)
            return
        folder = Path(path)
        filtered = [t for t in self._all_tracks if folder in t.path.parents or t.path.parent == folder]
        self._library_model.load_tracks(filtered)
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
