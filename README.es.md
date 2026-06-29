[English](README.md) · [Português](README.pt-BR.md) · **Español** · [中文](README.zh.md)

---

# IG Baixador

Descargador personal de contenido de Instagram para escritorio (Windows y macOS).
Funciona **en tu PC, desde tu IP y con tu sesión iniciada** — por eso sigue funcionando cuando los sitios públicos de descarga (SnapInsta, iGram, etc.) están caídos.

Pega uno o varios enlaces y descarga todo de una sola vez. Los videos se generan como un **único MP4 con sonido** (ffmpeg integrado — no tienes que instalar nada).

## Qué descarga
- **Reels y videos** (la función principal) — MP4 con audio
- Fotos y carruseles del feed
- Historias y destacados (con las cookies configuradas)
- Perfil completo (pega el enlace del perfil)

## Cómo usar
1. Abre **IG Baixador** (Windows: `IG-Baixador.exe`; Mac: abre el `.dmg`, arrastra la app y, **la primera vez, clic derecho → Abrir**).
2. **Cookies (la primera vez):** Instagram solo entrega el contenido con la sesión iniciada, y Chrome no permite leer las cookies automáticamente. Así que:
   - Instala la extensión **"Get cookies.txt LOCALLY"** en Chrome (gratuita, se ejecuta de forma local).
   - Abre `instagram.com` con tu sesión iniciada y, con esa pestaña al frente, haz clic en el icono de la extensión → **Export**.
   - En la app, haz clic en **"Seleccionar cookies.txt"** y elige el archivo descargado.
   - El botón **"❔ Cómo usar"** dentro de la app incluye este paso a paso.
3. Pega uno o varios enlaces (uno por línea) y haz clic en **"Descargar todo"**. Cada enlace se convierte en una fila de la cola con su progreso.

## Desarrollar

Requiere Python 3.11+.

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements-dev.txt   # pytest, pyinstaller
.venv\Scripts\pip install -r requirements.txt       # customtkinter

# Binarios externos integrados (no versionados) — descárgalos en bin/win/:
curl -L -o bin/win/gallery-dl.exe https://github.com/mikf/gallery-dl/releases/download/v1.31.10/gallery-dl.exe
curl -L -o bin/win/yt-dlp.exe     https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe
# + ffmpeg.exe y ffprobe.exe (p. ej. un build estático de gyan.dev) en bin/win/

.venv\Scripts\python -m pytest -q          # pruebas
.venv\Scripts\python -m ig_baixador        # abre la ventana

# Build del .exe (ejecutar desde la raíz del repo):
.venv\Scripts\pyinstaller build\ig-baixador.spec --noconfirm --distpath dist --workpath build\work
```

La app de **macOS** (`.dmg`) se genera mediante GitHub Actions (workflow `build-mac.yml`), en un runner de macOS — no es posible compilar la app de Mac desde Windows.

## Cómo funciona
Una carcasa en **customtkinter** (la interfaz) sobre **gallery-dl** (el motor principal), con **yt-dlp** como respaldo y **ffmpeg** para unir audio+video. La sesión proviene únicamente de las cookies (del navegador o de un archivo `cookies.txt`) — la app **nunca pide usuario ni contraseña**.
