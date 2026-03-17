"""Download audio from YouTube using yt-dlp."""

import subprocess
from pathlib import Path


class DownloadError(Exception):
    """Raised when a yt-dlp download fails."""


def _files_in(directory: Path) -> set[Path]:
    """Return the set of files currently in a directory."""
    if not directory.is_dir():
        return set()
    return {p for p in directory.iterdir() if p.is_file()}


def download_video_audio(video_id: str, output_dir: Path) -> Path:
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
        "--no-playlist",
        "--extract-audio",
        "--audio-format", "best",
        "--output", template,
        url,
    ]

    try:
        subprocess.run(
            cmd, capture_output=True, text=True, check=True,
        )
    except FileNotFoundError:
        raise DownloadError("yt-dlp is not installed. Install it with: pip install yt-dlp")
    except subprocess.CalledProcessError as e:
        raise DownloadError(f"yt-dlp failed: {e.stderr.strip()}")

    new_files = _files_in(output_dir) - before
    if not new_files:
        raise DownloadError("yt-dlp did not produce any output files.")

    return max(new_files, key=lambda p: p.stat().st_mtime)


def download_playlist_audio(playlist_id: str, output_dir: Path) -> list[Path]:
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
        "--extract-audio",
        "--audio-format", "best",
        "--output", template,
        url,
    ]

    try:
        subprocess.run(
            cmd, capture_output=True, text=True, check=True,
        )
    except FileNotFoundError:
        raise DownloadError("yt-dlp is not installed. Install it with: pip install yt-dlp")
    except subprocess.CalledProcessError as e:
        raise DownloadError(f"yt-dlp failed: {e.stderr.strip()}")

    new_files = _files_in(output_dir) - before
    if not new_files:
        raise DownloadError("yt-dlp did not produce any output files.")

    return sorted(new_files, key=lambda p: p.stat().st_mtime)
