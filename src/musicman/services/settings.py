"""QSettings wrapper for application preferences."""

from PySide6.QtCore import QSettings


class Settings:
    def __init__(self):
        self._s = QSettings("MusicMan", "MusicMan")

    @property
    def library_root(self) -> str:
        return self._s.value("library/root", "", type=str)

    @library_root.setter
    def library_root(self, value: str):
        self._s.setValue("library/root", value)

    @property
    def device_path(self) -> str:
        return self._s.value("device/path", "", type=str)

    @device_path.setter
    def device_path(self, value: str):
        self._s.setValue("device/path", value)

    @property
    def transcode_mode(self) -> str:
        """'cbr' or 'vbr'."""
        return self._s.value("transcode/mode", "cbr", type=str)

    @transcode_mode.setter
    def transcode_mode(self, value: str):
        self._s.setValue("transcode/mode", value)

    @property
    def cbr_bitrate(self) -> int:
        return self._s.value("transcode/cbr_bitrate", 192, type=int)

    @cbr_bitrate.setter
    def cbr_bitrate(self, value: int):
        self._s.setValue("transcode/cbr_bitrate", value)

    @property
    def vbr_quality(self) -> int:
        return self._s.value("transcode/vbr_quality", 2, type=int)

    @vbr_quality.setter
    def vbr_quality(self, value: int):
        self._s.setValue("transcode/vbr_quality", value)

    def save_geometry(self, geometry: bytes):
        self._s.setValue("window/geometry", geometry)

    def load_geometry(self) -> bytes | None:
        return self._s.value("window/geometry")

    def save_state(self, state: bytes):
        self._s.setValue("window/state", state)

    def load_state(self) -> bytes | None:
        return self._s.value("window/state")
