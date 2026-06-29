**English** · [Português](README.pt-BR.md) · [Español](README.es.md) · [中文](README.zh.md)

---

# IG Baixador

Personal Instagram content downloader for desktop (Windows and macOS).
It runs **on your own PC, from your own IP, and using your own logged-in session** — which is why it works even when the public download sites (SnapInsta, iGram, etc.) are down.

Paste one or several links and download them all at once. Videos come out as a **single MP4 with sound** (ffmpeg is bundled — you don't install anything).

## What it downloads
- **Reels and videos** (the main focus) — MP4 with audio
- Feed photos and carousels
- Stories and highlights (with cookies set up)
- An entire profile (just paste the profile link)

## How to use
1. Open **IG Baixador** (Windows: `IG-Baixador.exe`; Mac: open the `.dmg`, drag the
   app in, and **the first time, right-click → Open**).
2. **Cookies (first time):** Instagram only serves content when you're logged in, and
   Chrome won't let the app read its cookies automatically. So:
   - Install the **"Get cookies.txt LOCALLY"** extension in Chrome (free, runs locally).
   - Open `instagram.com` while logged in and, with that tab in front, click the
     extension's icon → **Export**.
   - In the app, click **"Select cookies.txt"** and choose the file you downloaded.
   - The **"❔ How to use"** button inside the app walks you through these same steps.
3. Paste one or more links (one per line) and click **"Download all"**. Each link
   becomes a row in the queue showing its progress.

## Development

Requires Python 3.11+.

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements-dev.txt   # pytest, pyinstaller
.venv\Scripts\pip install -r requirements.txt       # customtkinter

# Bundled external binaries (not versioned) — download them into bin/win/:
curl -L -o bin/win/gallery-dl.exe https://github.com/mikf/gallery-dl/releases/download/v1.31.10/gallery-dl.exe
curl -L -o bin/win/yt-dlp.exe     https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe
# + ffmpeg.exe and ffprobe.exe (e.g. a static build from gyan.dev) in bin/win/

.venv\Scripts\python -m pytest -q          # tests
.venv\Scripts\python -m ig_baixador        # launches the window

# Build the .exe (run from the repo root):
.venv\Scripts\pyinstaller build\ig-baixador.spec --noconfirm --distpath dist --workpath build\work
```

The **macOS** app (`.dmg`) is built by GitHub Actions (the `build-mac.yml` workflow)
on a macOS runner — you can't compile the Mac app from Windows.

## How it works
A **customtkinter** shell (the interface) sits on top of **gallery-dl** (the main engine), with
**yt-dlp** as a fallback and **ffmpeg** to merge audio and video. The session comes purely from cookies
(either from the browser or from a `cookies.txt` file) — the app **never asks for a username or password**.
