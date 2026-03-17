"""Transfer orchestrator: copy MP3s, transcode others, apply prefixes."""

import shutil
from pathlib import Path

from musicman.models.track import Track
from musicman.models.transfer_queue import generate_prefix, sanitize_filename
from musicman.services.transcoder import transcode


def transfer_tracks(
    tracks: list[Track],
    device_path: Path,
    mode: str = "cbr",
    cbr_bitrate: int = 192,
    vbr_quality: int = 2,
    progress_callback=None,
    cancel_check=None,
) -> list[str]:
    """
    Transfer tracks to device with prefix naming.

    Args:
        tracks: Ordered list of tracks to transfer.
        device_path: Target directory on device.
        mode: 'cbr' or 'vbr'.
        cbr_bitrate: CBR bitrate in kbps.
        vbr_quality: VBR quality level (0-9).
        progress_callback: Called with (index, total, filename) for each track.
        cancel_check: Callable returning True if cancelled.

    Returns:
        List of error messages (empty on full success).
    """
    errors = []
    total = len(tracks)

    for i, track in enumerate(tracks):
        if cancel_check and cancel_check():
            errors.append("Transfer cancelled.")
            break

        prefix = generate_prefix(i)
        title = sanitize_filename(track.display_title)
        out_name = f"{prefix}_{title}.mp3"
        out_path = device_path / out_name

        if progress_callback:
            progress_callback(i, total, out_name)

        try:
            if track.format == "mp3":
                shutil.copy2(track.path, out_path)
            else:
                transcode(
                    track.path,
                    out_path,
                    mode=mode,
                    cbr_bitrate=cbr_bitrate,
                    vbr_quality=vbr_quality,
                )
        except Exception as e:
            errors.append(f"{track.display_title}: {e}")

    return errors
