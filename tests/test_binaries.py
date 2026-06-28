import pytest
from ig_baixador.binaries import binary_filename


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
