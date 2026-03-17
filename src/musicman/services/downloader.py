"""Download audio from YouTube using yt-dlp."""

import subprocess
from pathlib import Path
from typing import Callable


class DownloadError(Exception):
    """Raised when a yt-dlp download fails."""


def _files_in(directory: Path) -> set[Path]:
    """Return the set of files currently in a directory."""
    if not directory.is_dir():
        return set()
    return {p for p in directory.iterdir() if p.is_file()}


def _run_ytdlp(cmd: list[str], process_callback: Callable | None = None) -> None:
    """Run a yt-dlp command, optionally exposing the Popen object via callback."""
    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
    except FileNotFoundError:
        raise DownloadError("yt-dlp is not installed. Install it with: pip install yt-dlp")

    if process_callback:
        process_callback(proc)

    _, stderr = proc.communicate()

    if proc.returncode != 0:
        raise DownloadError(f"yt-dlp failed: {stderr.strip()}")


def download_video_audio(
    video_id: str,
    output_dir: Path,
    process_callback: Callable | None = None,
) -> Path:
    """Download audio for a single YouTube video into output_dir.

    Returns the path of the downloaded file.
    Raises DownloadError on failure.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    template = str(output_dir / "%(title)s.%(ext)s")
    url = f"https://www.youtube.com/watch?v={video_id}"

    before = _files_in(output_dir)

    cmd = [
        "yt-dlp",
        "--ignore-config",
        "--no-playlist",
        "--extract-audio",
        "--audio-format", "best",
        "--embed-metadata",
        "--output", template,
        url,
    ]

    _run_ytdlp(cmd, process_callback)

    new_files = _files_in(output_dir) - before
    if not new_files:
        raise DownloadError("yt-dlp did not produce any output files.")

    return max(new_files, key=lambda p: p.stat().st_mtime)


def download_playlist_audio(
    playlist_id: str,
    output_dir: Path,
    process_callback: Callable | None = None,
) -> list[Path]:
    """Download audio for all videos in a YouTube playlist.

    Returns a list of paths for the downloaded files.
    Raises DownloadError on failure.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    template = str(output_dir / "%(title)s.%(ext)s")
    url = f"https://www.youtube.com/playlist?list={playlist_id}"

    before = _files_in(output_dir)

    cmd = [
        "yt-dlp",
        "--ignore-config",
        "--extract-audio",
        "--audio-format", "best",
        "--embed-metadata",
        "--output", template,
        url,
    ]

    _run_ytdlp(cmd, process_callback)

    new_files = _files_in(output_dir) - before
    if not new_files:
        raise DownloadError("yt-dlp did not produce any output files.")

    return sorted(new_files, key=lambda p: p.stat().st_mtime)
