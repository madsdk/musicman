"""Tests for the ffmpeg transcoder command construction."""

from pathlib import Path

from musicman.services.transcoder import build_ffmpeg_command


class TestBuildFfmpegCommand:
    def test_cbr_default(self):
        cmd = build_ffmpeg_command(Path("/in.flac"), Path("/out.mp3"))
        assert cmd[0] == "ffmpeg"
        assert "-y" in cmd
        assert "-i" in cmd
        assert "/in.flac" in cmd
        assert "-b:a" in cmd
        assert "192k" in cmd
        assert cmd[-1] == "/out.mp3"

    def test_cbr_320(self):
        cmd = build_ffmpeg_command(
            Path("/in.wav"), Path("/out.mp3"), mode="cbr", cbr_bitrate=320
        )
        assert "320k" in cmd

    def test_vbr(self):
        cmd = build_ffmpeg_command(
            Path("/in.ogg"), Path("/out.mp3"), mode="vbr", vbr_quality=4
        )
        assert "-qscale:a" in cmd
        assert "4" in cmd
        assert "-b:a" not in cmd

    def test_no_video(self):
        cmd = build_ffmpeg_command(Path("/in.flac"), Path("/out.mp3"))
        assert "-vn" in cmd
