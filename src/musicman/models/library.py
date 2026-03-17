"""Hierarchical Artist > Album > Track tree model for the library."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItem, QStandardItemModel

from musicman.models.track import Track

TRACK_ROLE = Qt.ItemDataRole.UserRole + 1


class LibraryModel(QStandardItemModel):
    """Tree model: Artist > Album > Track."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalHeaderLabels(["Library", "Duration"])

    def load_tracks(self, tracks: list[Track]):
        """Build the tree from a flat list of tracks."""
        self.clear()
        self.setHorizontalHeaderLabels(["Library", "Duration"])

        # Group: artist -> album -> [tracks]
        tree: dict[str, dict[str, list[Track]]] = {}
        for t in tracks:
            tree.setdefault(t.artist, {}).setdefault(t.album, []).append(t)

        root = self.invisibleRootItem()
        for artist_name in sorted(tree):
            artist_item = QStandardItem(artist_name)
            artist_item.setEditable(False)
            artist_dur = QStandardItem()
            artist_dur.setEditable(False)

            for album_name in sorted(tree[artist_name]):
                album_item = QStandardItem(album_name)
                album_item.setEditable(False)
                album_dur = QStandardItem()
                album_dur.setEditable(False)

                for track in sorted(tree[artist_name][album_name], key=lambda t: t.title):
                    track_item = QStandardItem(track.display_title)
                    track_item.setEditable(False)
                    track_item.setData(track, TRACK_ROLE)
                    dur_item = QStandardItem(track.duration_str)
                    dur_item.setEditable(False)
                    album_item.appendRow([track_item, dur_item])

                artist_item.appendRow([album_item, album_dur])

            root.appendRow([artist_item, artist_dur])

    def get_tracks_for_index(self, index) -> list[Track]:
        """Get all Track objects under a given model index."""
        item = self.itemFromIndex(index)
        if item is None:
            return []
        return self._collect_tracks(item)

    def _collect_tracks(self, item: QStandardItem) -> list[Track]:
        track = item.data(TRACK_ROLE)
        if track is not None:
            return [track]
        tracks = []
        for row in range(item.rowCount()):
            child = item.child(row, 0)
            if child:
                tracks.extend(self._collect_tracks(child))
        return tracks
