"""Resolução dos argumentos de cookie para gallery-dl e yt-dlp."""
from __future__ import annotations

from pathlib import Path

from .config import Config


def cookie_args(cfg: Config) -> list[str]:
    if cfg.cookie_mode == "chrome":
        return ["--cookies-from-browser", "chrome"]
    if cfg.cookie_mode == "cookies_txt":
        return ["--cookies", cfg.cookies_txt_path]
    # auto
    if cfg.cookies_txt_path and Path(cfg.cookies_txt_path).is_file():
        return ["--cookies", cfg.cookies_txt_path]
    return ["--cookies-from-browser", "chrome"]
