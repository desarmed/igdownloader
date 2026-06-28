from pathlib import Path
from ig_baixador.config import Config, default_config, load_config, save_config


def test_default_config_values():
    cfg = default_config()
    assert cfg.cookie_mode == "auto"
    assert cfg.cookies_txt_path == ""
    assert cfg.dest_dir.endswith("IG-Baixador")


def test_load_missing_returns_default(tmp_path):
    cfg = load_config(tmp_path / "nope.json")
    assert cfg.cookie_mode == "auto"


def test_save_then_load_roundtrip(tmp_path):
    p = tmp_path / "config.json"
    cfg = Config(dest_dir="D:/baixados", cookie_mode="chrome", cookies_txt_path="")
    save_config(cfg, p)
    loaded = load_config(p)
    assert loaded == cfg
