#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Verify ffmpeg is available on the build machine
if ! command -v ffmpeg &>/dev/null; then
    echo "ERROR: ffmpeg not found. Install it before building." >&2
    exit 1
fi

echo "Building MusicMan.app with PyInstaller..."
pyinstaller MusicMan.spec

echo ""
echo "Done! App bundle is at:"
echo "  dist/MusicMan.app"
