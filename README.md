# MusicMan

A PySide6 desktop app for managing music on old-school MP3 players that play files in alphabetical filename order. MusicMan handles library browsing, transcoding, and automatic track ordering via two-letter filename prefixes (AA–ZZ).

## Prerequisites

- Python 3.10+
- ffmpeg (for transcoding non-MP3 files)

Install ffmpeg via your package manager:

```bash
# Arch
sudo pacman -S ffmpeg

# Debian/Ubuntu
sudo apt install ffmpeg

# Fedora
sudo dnf install ffmpeg
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

On first launch, open **File > Settings** to set your library root folder. The app will scan it recursively for MP3, FLAC, OGG, WAV, AAC, and WMA files.

## Usage

1. **Library** (left panel) — Browse by folder or by Artist > Album > Track. Select nodes and click "Add to Queue >>" or double-click a track.
2. **Transfer Queue** (center panel) — Drag-and-drop to reorder. Tracks get auto-assigned "AA", "AB", ... "ZZ" prefixes (676 max). Click "Transfer" to copy/transcode to the device.
3. **Device** (right panel) — Lists files on the selected device. Delete files with confirmation.

The device selector bar at the top auto-detects removable volumes mounted under `/media`, `/run/media`, or `/mnt`. You can also type or browse to a path manually.

## Development

Install with dev dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest tests/ -v
```

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
    └── transfer_worker.py   # Background transfer with progress
```
