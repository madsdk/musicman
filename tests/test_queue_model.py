"""Tests for the transfer queue model."""

from pathlib import Path

from musicman.models.track import Track
from musicman.models.transfer_queue import TransferQueueModel


def _track(title="Song", artist="Artist", fmt="mp3"):
    return Track(path=Path(f"/music/{title}.{fmt}"), title=title, artist=artist, format=fmt)


class TestTransferQueueModel:
    def test_add_tracks(self):
        model = TransferQueueModel()
        model.add_tracks([_track("A"), _track("B")])
        assert model.rowCount() == 2

    def test_prefix_assignment(self):
        model = TransferQueueModel()
        model.add_tracks([_track(f"Song{i}") for i in range(3)])
        assert model.data(model.index(0, 1)) == "AA"
        assert model.data(model.index(1, 1)) == "AB"
        assert model.data(model.index(2, 1)) == "AC"

    def test_remove_track(self):
        model = TransferQueueModel()
        model.add_tracks([_track("A"), _track("B"), _track("C")])
        model.remove_track(1)
        assert model.rowCount() == 2
        assert model.data(model.index(0, 2)) == "A"
        assert model.data(model.index(1, 2)) == "C"

    def test_clear(self):
        model = TransferQueueModel()
        model.add_tracks([_track("A"), _track("B")])
        model.clear()
        assert model.rowCount() == 0

    def test_output_filename(self):
        model = TransferQueueModel()
        model.add_tracks([_track("My Song")])
        fname = model.get_output_filename(0)
        assert fname == "AA_My Song.mp3"

    def test_display_data(self):
        model = TransferQueueModel()
        t = _track("Hello", "World")
        model.add_tracks([t])
        assert model.data(model.index(0, 0)) == 1  # row number
        assert model.data(model.index(0, 1)) == "AA"  # prefix
        assert model.data(model.index(0, 2)) == "Hello"  # title
        assert model.data(model.index(0, 3)) == "World"  # artist
