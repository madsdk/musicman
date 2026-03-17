"""Download audio from YouTube using yt-dlp."""

import threading
from pathlib import Path

import yt_dlp

from musicman.services.paths import get_binary


class DownloadError(Exception):
    """Raised when a yt-dlp download fails."""


def _files_in(directory: Path) -> set[Path]:
    """Return the set of files currently in a directory."""
    if not directory.is_dir():
        return set()
    return {p for p in directory.iterdir() if p.is_file()}


def _base_opts(template: str) -> dict:
    """Return yt-dlp options common to single-video and playlist downloads."""
    ffmpeg = get_binary("ffmpeg")
    opts: dict = {
        "format": "bestaudio/best",
        "postprocessors": [
            {"key": "FFmpegExtractAudio", "preferredcodec": "best"},
            {"key": "FFmpegMetadata"},
        ],
        "outtmpl": template,
        "quiet": True,
        "no_warnings": True,
    }
    if ffmpeg != "ffmpeg":
        opts["ffmpeg_location"] = str(Path(ffmpeg).parent)
    return opts


def _run_ytdlp(
    url: str,
    opts: dict,
    cancel_event: threading.Event | None = None,
) -> None:
    """Run a yt-dlp download, checking cancel_event between entries."""
    if cancel_event and cancel_event.is_set():
        raise DownloadError("Download cancelled")

    def _progress_hook(d: dict) -> None:
        if cancel_event and cancel_event.is_set():
            raise DownloadError("Download cancelled")

    opts["progress_hooks"] = [_progress_hook]

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            ret = ydl.download([url])
    except DownloadError:
        raise
    except Exception as e:
        raise DownloadError(f"yt-dlp failed: {e}")

    if ret != 0:
        raise DownloadError("yt-dlp failed with a non-zero exit code.")


def download_video_audio(
    video_id: str,
    output_dir: Path,
    cancel_event: threading.Event | None = None,
) -> Path:
    """Download audio for a single YouTube video into output_dir.

    Returns the path of the downloaded file.
    Raises DownloadError on failure.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    template = str(output_dir / "%(title)s.%(ext)s")
    url = f"https://www.youtube.com/watch?v={video_id}"

    before = _files_in(output_dir)

    opts = _base_opts(template)
    opts["noplaylist"] = True

    _run_ytdlp(url, opts, cancel_event)

    new_files = _files_in(output_dir) - before
    if not new_files:
        raise DownloadError("yt-dlp did not produce any output files.")

    return max(new_files, key=lambda p: p.stat().st_mtime)


def download_playlist_audio(
    playlist_id: str,
    output_dir: Path,
    cancel_event: threading.Event | None = None,
) -> list[Path]:
    """Download audio for all videos in a YouTube playlist.

    Returns a list of paths for the downloaded files.
    Raises DownloadError on failure.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    template = str(output_dir / "%(title)s.%(ext)s")
    url = f"https://www.youtube.com/playlist?list={playlist_id}"

    before = _files_in(output_dir)

    opts = _base_opts(template)

    _run_ytdlp(url, opts, cancel_event)

    new_files = _files_in(output_dir) - before
    if not new_files:
        raise DownloadError("yt-dlp did not produce any output files.")

    return sorted(new_files, key=lambda p: p.stat().st_mtime)
