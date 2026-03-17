# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for MusicMan macOS .app bundle."""

import shutil
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# --- Locate system binaries to bundle ---
ffmpeg_path = shutil.which("ffmpeg")
ffprobe_path = shutil.which("ffprobe")

binaries = []
if ffmpeg_path:
    binaries.append((ffmpeg_path, "."))
if ffprobe_path:
    binaries.append((ffprobe_path, "."))

# --- Collect packages that need special handling ---
mutagen_datas, mutagen_binaries, mutagen_hiddenimports = collect_all("mutagen")
ytdlp_datas, ytdlp_binaries, ytdlp_hiddenimports = collect_all("yt_dlp")

a = Analysis(
    ["src/musicman/__main__.py"],
    pathex=[],
    binaries=binaries + mutagen_binaries + ytdlp_binaries,
    datas=mutagen_datas + ytdlp_datas,
    hiddenimports=mutagen_hiddenimports + ytdlp_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="MusicMan",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="MusicMan",
)

app = BUNDLE(
    coll,
    name="MusicMan.app",
    icon=None,
    bundle_identifier="com.musicman.app",
)
