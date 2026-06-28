"""Detecção e normalização de URLs do Instagram."""
from __future__ import annotations

from urllib.parse import urlparse, urlunparse

_IG_HOSTS = {"instagram.com", "www.instagram.com", "m.instagram.com"}


def is_instagram_url(url: str) -> bool:
    try:
        parsed = urlparse(url if "://" in url else "https://" + url)
    except ValueError:
        return False
    if " " in url or not parsed.netloc:
        return False
    return parsed.netloc.lower() in _IG_HOSTS


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path
    if not path.endswith("/"):
        path += "/"
    return urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))


def detect_url_type(url: str) -> str:
    if not is_instagram_url(url):
        return "unknown"
    parts = [p for p in urlparse(url).path.split("/") if p]
    if not parts:
        return "unknown"
    head = parts[0].lower()
    if head in ("reel", "reels"):
        return "reel"
    if head == "p":
        return "post"
    if head == "stories":
        if len(parts) >= 2 and parts[1].lower() == "highlights":
            return "highlight"
        return "story"
    return "profile"
