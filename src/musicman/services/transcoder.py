"""FFmpeg wrapper for transcoding audio files to MP3."""

import shutil
import subprocess
from pathlib import Path


class TranscodeError(Exception):
    pass


def check_ffmpeg() -> bool:
    """Check if ffmpeg is available."""
    return shutil.which("ffmpeg") is not None


def build_ffmpeg_command(
    input_path: Path,
    output_path: Path,
    mode: str = "cbr",
    cbr_bitrate: int = 192,
    vbr_quality: int = 2,
) -> list[str]:
    """Build the ffmpeg command for transcoding to MP3."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vn",  # no video
    ]
    if mode == "vbr":
        cmd.extend(["-codec:a", "libmp3lame", "-qscale:a", str(vbr_quality)])
    else:
        cmd.extend(["-codec:a", "libmp3lame", "-b:a", f"{cbr_bitrate}k"])
    cmd.append(str(output_path))
    return cmd


def transcode(
    input_path: Path,
    output_path: Path,
    mode: str = "cbr",
    cbr_bitrate: int = 192,
    vbr_quality: int = 2,
) -> None:
    """Transcode an audio file to MP3 using ffmpeg."""
    cmd = build_ffmpeg_command(input_path, output_path, mode, cbr_bitrate, vbr_quality)
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,
        )
        if result.returncode != 0:
            raise TranscodeError(f"ffmpeg failed: {result.stderr[-500:]}")
    except FileNotFoundError:
        raise TranscodeError("ffmpeg not found. Please install ffmpeg.")
    except subprocess.TimeoutExpired:
        raise TranscodeError("Transcode timed out after 5 minutes.")
