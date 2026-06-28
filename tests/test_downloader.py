from ig_baixador.config import Config
from ig_baixador.downloader import (
    build_gallery_dl_cmd, build_ytdlp_cmd, classify_error,
    download, DownloadResult,
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


def test_classify_cookies_locked_permission_denied():
    code, msg = classify_error("", "Permission denied: cookies.db", 1)
    assert code == "cookies_locked"


def test_classify_private():
    code, msg = classify_error("", "Requested content is not available", 1)
    assert code == "private"


def test_classify_ok():
    code, msg = classify_error("1 file downloaded", "", 0)
    assert code == "ok"


def _cfg():
    return Config(dest_dir="D:/out", cookie_mode="chrome", cookies_txt_path="")


def test_download_rejects_non_instagram():
    res = download("https://youtube.com/x", _cfg(), runner=lambda cmd: (0, "", ""))
    assert res.ok is False
    assert res.code == "not_instagram"


def test_download_success_first_try():
    calls = []
    def runner(cmd):
        calls.append(cmd)
        return (0, "1 file downloaded", "")
    res = download("https://www.instagram.com/reel/Cabc/", _cfg(), runner=runner)
    assert res.ok is True
    assert res.code == "ok"
    assert len(calls) == 1  # não precisou de fallback


def test_download_falls_back_to_ytdlp_for_reel():
    calls = []
    def runner(cmd):
        calls.append(cmd)
        # 1ª chamada (gallery-dl) falha, 2ª (yt-dlp) dá certo
        if len(calls) == 1:
            return (1, "", "some error")
        return (0, "[download] 100%", "")
    res = download("https://www.instagram.com/reel/Cabc/", _cfg(), runner=runner)
    assert res.ok is True
    assert len(calls) == 2
    assert "yt-dlp" in calls[1][0]


def test_download_login_error_no_fallback_loops():
    calls = []
    def runner(cmd):
        calls.append(cmd)
        return (1, "", "401 Unauthorized")
    res = download("https://www.instagram.com/reel/Cabc/", _cfg(), runner=runner)
    assert res.ok is False
    assert res.code == "login"


def test_download_runner_exception_returns_result():
    def runner(cmd):
        raise FileNotFoundError("binary not found")
    res = download("https://www.instagram.com/reel/Cabc/", _cfg(), runner=runner)
    assert isinstance(res, DownloadResult)
    assert res.ok is False
