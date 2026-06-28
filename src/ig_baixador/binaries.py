"""Localização dos binários embutidos (gallery-dl, yt-dlp) por plataforma."""
from __future__ import annotations

import os
import stat
import sys
from pathlib import Path

_NAMES = {
    "win32": {"gallery-dl": "gallery-dl.exe", "yt-dlp": "yt-dlp.exe"},
    "darwin": {"gallery-dl": "gallery-dl.bin", "yt-dlp": "yt-dlp_macos"},
}
_PLATFORM_DIR = {"win32": "win", "darwin": "mac"}


def binary_filename(tool: str, platform: str) -> str:
    try:
        return _NAMES[platform][tool]
    except KeyError:
        raise ValueError(f"binário desconhecido: tool={tool!r} platform={platform!r}")


def binaries_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS")) / "bin"
    return Path(__file__).resolve().parents[2] / "bin"


def platform_bin_dir() -> Path:
    """Retorna o diretório de binários da plataforma atual."""
    platform = sys.platform
    sub = _PLATFORM_DIR.get(platform)
    if sub is None:
        raise ValueError(f"plataforma não suportada: {platform!r}")
    return binaries_base_dir() / sub


def resolve_binary(tool: str) -> Path:
    platform = sys.platform
    sub = _PLATFORM_DIR.get(platform)
    if sub is None:
        raise ValueError(f"plataforma não suportada: {platform!r}")
    path = binaries_base_dir() / sub / binary_filename(tool, platform)
    if getattr(sys, "frozen", False) and sys.platform != "win32" and path.exists():
        mode = path.stat().st_mode
        if not (mode & stat.S_IXUSR):
            os.chmod(path, mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path
