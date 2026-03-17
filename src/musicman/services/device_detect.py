"""Removable volume detection for Linux."""

from pathlib import Path


def detect_removable_volumes() -> list[tuple[str, str]]:
    """Return list of (label, mount_path) for removable volumes."""
    volumes = []
    search_dirs = [
        Path("/media"),
        Path("/run/media"),
        Path("/mnt"),
    ]
    for base in search_dirs:
        if not base.is_dir():
            continue
        # /media/<user>/<volume> or /run/media/<user>/<volume>
        for entry in base.iterdir():
            if entry.is_dir():
                if entry.is_mount():
                    volumes.append((entry.name, str(entry)))
                else:
                    # Check subdirectories (e.g. /media/user/DEVICE)
                    for sub in entry.iterdir():
                        if sub.is_dir() and sub.is_mount():
                            volumes.append((sub.name, str(sub)))
    return sorted(set(volumes))
