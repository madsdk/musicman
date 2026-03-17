"""Download audio from YouTube using yt-dlp."""

import subprocess
from pathlib import Path


class DownloadError(Exception):
    """Raised when a yt-dlp download fails."""


def download_audio(url: str, output_dir: Path) -> Path:
    """Download audio from a YouTube URL into output_dir.

    Returns the path of the downloaded file.
    Raises DownloadError on failure.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    template = str(output_dir / "%(title)s.%(ext)s")

    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "best",
        "--output", template,
        "--print", "after_move:filepath",
        url,
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True,
        )
    except FileNotFoundError:
        raise DownloadError("yt-dlp is not installed. Install it with: pip install yt-dlp")
    except subprocess.CalledProcessError as e:
        raise DownloadError(f"yt-dlp failed: {e.stderr.strip()}")

    # The last non-empty line of stdout is the filepath
    lines = [line.strip() for line in result.stdout.strip().splitlines() if line.strip()]
    if not lines:
        raise DownloadError("yt-dlp did not report an output file path.")

    filepath = Path(lines[-1])
    if not filepath.is_file():
        raise DownloadError(f"Downloaded file not found: {filepath}")

    return filepath
