import pytest
from ig_baixador.urls import is_instagram_url, detect_url_type, normalize_url


@pytest.mark.parametrize("url,expected", [
    ("https://www.instagram.com/reel/Cabc123/", True),
    ("https://instagram.com/p/Cxyz/", True),
    ("http://instagram.com/user", True),
    ("https://youtube.com/watch?v=x", False),
    ("not a url", False),
    ("", False),
])
def test_is_instagram_url(url, expected):
    assert is_instagram_url(url) == expected


@pytest.mark.parametrize("url,expected", [
    ("https://www.instagram.com/reel/Cabc123/", "reel"),
    ("https://www.instagram.com/reels/Cabc123/", "reel"),
    ("https://www.instagram.com/p/Cxyz/", "post"),
    ("https://www.instagram.com/stories/someuser/123456/", "story"),
    ("https://www.instagram.com/stories/highlights/178/", "highlight"),
    ("https://www.instagram.com/someuser/", "profile"),
    ("https://www.instagram.com/", "unknown"),
])
def test_detect_url_type(url, expected):
    assert detect_url_type(url) == expected


def test_normalize_strips_query_and_fragment():
    assert normalize_url("https://www.instagram.com/reel/Cabc/?igsh=xyz#frag") == \
        "https://www.instagram.com/reel/Cabc/"


def test_normalize_adds_trailing_slash():
    assert normalize_url("https://www.instagram.com/reel/Cabc") == \
        "https://www.instagram.com/reel/Cabc/"
