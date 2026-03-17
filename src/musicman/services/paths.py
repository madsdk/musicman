"""Resolve paths to bundled binaries (PyInstaller) or system commands."""

import os
import sys


def get_binary(name: str) -> str:
    """Return the path to a bundled binary, or the bare name for PATH lookup.

    When running inside a PyInstaller bundle, binaries are unpacked into
    sys._MEIPASS.  Outside a bundle this simply returns *name* so that
    subprocess can find it on the regular PATH.
    """
    if getattr(sys, "frozen", False):
        bundled = os.path.join(sys._MEIPASS, name)
        if os.path.isfile(bundled):
            return bundled
    return name
