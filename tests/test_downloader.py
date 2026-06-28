from ig_baixador.downloader import (
    build_gallery_dl_cmd, build_ytdlp_cmd, classify_error,
)


def test_build_gallery_dl_cmd():
    cmd = build_gallery_dl_cmd(
        "C:/bin/gallery-dl.exe",
        "https://www.instagram.com/reel/Cabc/",
        "D:/out",
        ["--cookies-from-browser", "chrome"],
    )
    assert cmd[0] == "C:/bin/gallery-dl.exe"
    assert "--cookies-from-browser" in cmd and "chrome" in cmd
    assert "-d" in cmd and "D:/out" in cmd
    assert cmd[-1] == "https://www.instagram.com/reel/Cabc/"


def test_build_ytdlp_cmd():
    cmd = build_ytdlp_cmd(
        "C:/bin/yt-dlp.exe",
        "https://www.instagram.com/reel/Cabc/",
        "D:/out",
        ["--cookies", "/c/ck.txt"],
    )
    assert cmd[0] == "C:/bin/yt-dlp.exe"
    assert "--cookies" in cmd and "/c/ck.txt" in cmd
    assert "-P" in cmd and "D:/out" in cmd
    assert cmd[-1].endswith("/reel/Cabc/")


def test_classify_login_required():
    code, msg = classify_error("", "HttpError: '401 Unauthorized'", 1)
    assert code == "login"
    assert "login" in msg.lower()


def test_classify_cookies_locked():
    code, msg = classify_error("", "Failed to decrypt with DPAPI", 1)
    assert code == "cookies_locked"
    assert "chrome" in msg.lower()


def test_classify_rate_limit():
    code, msg = classify_error("", "429 Too Many Requests", 1)
    assert code == "rate_limit"


def test_classify_private():
    code, msg = classify_error("", "Requested content is not available", 1)
    assert code == "private"


def test_classify_ok():
    code, msg = classify_error("1 file downloaded", "", 0)
    assert code == "ok"
