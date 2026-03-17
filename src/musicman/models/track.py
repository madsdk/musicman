"""Track dataclass for music file metadata."""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Track:
    path: Path
    title: str = ""
    artist: str = ""
    album: str = ""
    duration: float = 0.0  # seconds
    format: str = ""  # file extension without dot

    @property
    def duration_str(self) -> str:
        minutes = int(self.duration) // 60
        seconds = int(self.duration) % 60
        return f"{minutes}:{seconds:02d}"

    @property
    def display_title(self) -> str:
        return self.title or self.path.stem
