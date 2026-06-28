"""Carregamento e persistência da configuração do app."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class Config:
    dest_dir: str
    cookie_mode: str  # "auto" | "chrome" | "cookies_txt"
    cookies_txt_path: str


def default_config() -> Config:
    dest = Path.home() / "Downloads" / "IG-Baixador"
    return Config(dest_dir=str(dest), cookie_mode="auto", cookies_txt_path="")


def load_config(path: Path) -> Config:
    path = Path(path)
    if not path.exists():
        return default_config()
    data = json.loads(path.read_text(encoding="utf-8"))
    base = asdict(default_config())
    base.update({k: v for k, v in data.items() if k in base})
    return Config(**base)


def save_config(cfg: Config, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(asdict(cfg), indent=2), encoding="utf-8")
