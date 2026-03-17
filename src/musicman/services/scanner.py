"""Recursive music file scanner with mutagen metadata reading."""

from pathlib import Path

import mutagen

from musicman.models.track import Track

SUPPORTED_EXTENSIONS = {".mp3", ".flac", ".ogg", ".wav", ".aac", ".wma", ".opus", ".m4a", ".webm"}


def scan_directory(root: Path) -> list[Track]:
    """Recursively scan a directory for music files and read metadata."""
    tracks = []
    if not root.is_dir():
        return tracks

    for path in sorted(root.rglob("*")):
        if path.suffix.lower() in SUPPORTED_EXTENSIONS:
            track = read_track(path)
            if track:
                tracks.append(track)
    return tracks


def read_track(path: Path) -> Track | None:
    """Read metadata from a single music file."""
    try:
        audio = mutagen.File(path, easy=True)
    except Exception:
        return Track(path=path, format=path.suffix.lstrip(".").lower())

    if audio is None:
        return Track(path=path, format=path.suffix.lstrip(".").lower())

    title = _first(audio.get("title"))
    artist = _first(audio.get("artist"))
    album = _first(audio.get("album"))
    duration = audio.info.length if audio.info else 0.0

    return Track(
        path=path,
        title=title or path.stem,
        artist=artist or "Unknown Artist",
        album=album or "Unknown Album",
        duration=duration,
        format=path.suffix.lstrip(".").lower(),
    )


def _first(value) -> str:
    """Extract the first string from a tag value (mutagen returns lists)."""
    if isinstance(value, list) and value:
        return str(value[0])
    if isinstance(value, str):
        return value
    return ""
