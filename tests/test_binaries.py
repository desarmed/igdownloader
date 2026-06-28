import sys

import pytest
from ig_baixador.binaries import binary_filename, platform_bin_dir


@pytest.mark.parametrize("tool,platform,expected", [
    ("gallery-dl", "win32", "gallery-dl.exe"),
    ("yt-dlp", "win32", "yt-dlp.exe"),
    ("gallery-dl", "darwin", "gallery-dl.bin"),
    ("yt-dlp", "darwin", "yt-dlp_macos"),
])
def test_binary_filename(tool, platform, expected):
    assert binary_filename(tool, platform) == expected


def test_binary_filename_unknown_tool():
    with pytest.raises(ValueError):
        binary_filename("ffmpeg", "win32")


def test_platform_bin_dir_returns_path():
    p = platform_bin_dir()
    parts = p.parts
    # Last two segments must be ("bin", "win") on win32 or ("bin", "mac") on darwin
    if sys.platform == "win32":
        assert parts[-2] == "bin" and parts[-1] == "win", f"Unexpected path: {p}"
    elif sys.platform == "darwin":
        assert parts[-2] == "bin" and parts[-1] == "mac", f"Unexpected path: {p}"
    else:
        pytest.skip("Unsupported platform")
