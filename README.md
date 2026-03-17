# MusicMan

A PySide6 desktop app for managing music on old-school MP3 players that play files in alphabetical filename order. MusicMan handles library browsing, transcoding, and automatic track ordering via two-letter filename prefixes (AA–ZZ).

## Prerequisites

- Python 3.10+
- ffmpeg (for transcoding non-MP3 files)
- yt-dlp (optional, for downloading audio from YouTube)

Install system dependencies via your package manager:

```bash
# Arch
sudo pacman -S ffmpeg yt-dlp

# Debian/Ubuntu
sudo apt install ffmpeg
pip install yt-dlp

# Fedora
sudo dnf install ffmpeg
pip install yt-dlp
```

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Running

```bash
musicman
# or
python -m musicman
```

On first launch, open **File > Settings** to set your library root folder. The app will scan it recursively for MP3, FLAC, OGG, WAV, AAC, and WMA files. Optionally set a **download folder** to enable YouTube downloads.

## Usage

1. **Library** (left panel) — Browse by folder or by Artist > Album > Track. Select nodes and click "Add to Queue >>" or double-click a track.
2. **Transfer Queue** (center panel) — Drag-and-drop to reorder. Tracks get auto-assigned "AA", "AB", ... "ZZ" prefixes (676 max). Click "Transfer" to copy/transcode to the device.
3. **Device** (right panel) — Lists files on the selected device. Delete files with confirmation.

The device selector bar at the top auto-detects removable volumes mounted under `/media`, `/run/media`, or `/mnt`. You can also type or browse to a path manually.

### YouTube downloads

With a download folder configured in Settings and `yt-dlp` installed, enter a YouTube video ID or playlist ID into the bar below the device selector, select **Video** or **Playlist**, and click **Download**. The audio is extracted in the best available quality (no re-encode) and appears in the library under the **\<Downloads\>** artist. Downloaded tracks can be queued and transferred like any other track.

## Development

Install with dev dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest tests/ -v
```

### Building a macOS .app bundle

MusicMan can be packaged as a self-contained macOS application using PyInstaller. The bundle includes Python, PySide6, mutagen, yt-dlp, and ffmpeg — no external dependencies needed at runtime.

```bash
pip install -e ".[dev]"
bash scripts/build_macos.sh
```

The resulting app bundle is written to `dist/MusicMan.app`. You can drag it into `/Applications` or distribute it directly.

**Requirements for the build machine:**
- macOS with ffmpeg installed (bundled into the app automatically)
- yt-dlp installed (`pip install yt-dlp`) if you want YouTube download support in the bundle

### Project structure

```
src/musicman/
├── __main__.py              # Entry point
├── app.py                   # QApplication setup
├── models/
│   ├── track.py             # Track dataclass
│   ├── library.py           # Artist > Album > Track tree model
│   ├── device.py            # Device file listing model
│   └── transfer_queue.py    # Queue model with drag-drop + prefix generation
├── services/
│   ├── scanner.py           # Recursive scan + mutagen metadata
│   ├── transcoder.py        # ffmpeg wrapper
│   ├── transfer.py          # Transfer orchestrator
│   ├── downloader.py        # yt-dlp wrapper for YouTube audio
│   ├── device_detect.py     # Removable volume detection
│   └── settings.py          # QSettings wrapper
├── ui/
│   ├── main_window.py       # Main window with 3-panel splitter
│   ├── library_panel.py     # Folder tree + music tree
│   ├── queue_panel.py       # Transfer queue with reordering
│   ├── device_panel.py      # Device file browser
│   ├── device_selector.py   # Device combo/path/browse bar
│   ├── settings_dialog.py   # Preferences dialog
│   └── transfer_progress.py # Progress dialog
└── workers/
    ├── scan_worker.py       # Background library scan
    ├── download_worker.py   # Background YouTube download
    └── transfer_worker.py   # Background transfer with progress
```
