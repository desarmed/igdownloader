from ig_baixador.config import Config
from ig_baixador.cookies import cookie_args


def test_chrome_mode():
    cfg = Config(dest_dir="d", cookie_mode="chrome", cookies_txt_path="")
    assert cookie_args(cfg) == ["--cookies-from-browser", "chrome"]


def test_cookies_txt_mode():
    cfg = Config(dest_dir="d", cookie_mode="cookies_txt", cookies_txt_path="/c/ck.txt")
    assert cookie_args(cfg) == ["--cookies", "/c/ck.txt"]


def test_auto_prefers_existing_txt(tmp_path):
    ck = tmp_path / "cookies.txt"
    ck.write_text("x", encoding="utf-8")
    cfg = Config(dest_dir="d", cookie_mode="auto", cookies_txt_path=str(ck))
    assert cookie_args(cfg) == ["--cookies", str(ck)]


def test_auto_falls_back_to_chrome(tmp_path):
    cfg = Config(dest_dir="d", cookie_mode="auto", cookies_txt_path=str(tmp_path / "nope.txt"))
    assert cookie_args(cfg) == ["--cookies-from-browser", "chrome"]
