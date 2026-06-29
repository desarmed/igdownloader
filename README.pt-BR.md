[English](README.md) · **Português** · [Español](README.es.md) · [中文](README.zh.md)

---

# IG Baixador

Baixador pessoal de conteúdo do Instagram para desktop (Windows e macOS).
Roda **no seu PC, do seu IP e da sua sessão logada** — por isso funciona quando os
sites públicos de download (SnapInsta, iGram, etc.) estão fora do ar.

Cole um ou vários links e baixe de uma vez. Os vídeos saem como um **MP4 único com
som** (ffmpeg embutido — você não instala nada).

## O que baixa
- **Reels e vídeos** (foco principal) — MP4 com áudio
- Fotos e carrosséis do feed
- Stories e destaques (com cookies configurados)
- Perfil inteiro (cole o link do perfil)

## Como usar
1. Abra o **IG Baixador** (Windows: `IG-Baixador.exe`; Mac: abra o `.dmg`, arraste o
   app e, **na 1ª vez, botão direito → Abrir**).
2. **Cookies (1ª vez):** o Instagram só entrega conteúdo logado, e o Chrome não deixa
   ler os cookies automaticamente. Então:
   - Instale a extensão **"Get cookies.txt LOCALLY"** no Chrome (gratuita, roda local).
   - Abra o `instagram.com` logado e, com essa aba na frente, clique no ícone da
     extensão → **Export**.
   - No app, clique **"Selecionar cookies.txt"** e escolha o arquivo baixado.
   - O botão **"❔ Como usar"** dentro do app tem esse passo a passo.
3. Cole um ou vários links (um por linha) e clique **"Baixar tudo"**. Cada link vira
   uma linha na fila com o progresso.

## Desenvolver

Requer Python 3.11+.

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements-dev.txt   # pytest, pyinstaller
.venv\Scripts\pip install -r requirements.txt       # customtkinter

# Binários externos embutidos (não versionados) — baixe para bin/win/:
curl -L -o bin/win/gallery-dl.exe https://github.com/mikf/gallery-dl/releases/download/v1.31.10/gallery-dl.exe
curl -L -o bin/win/yt-dlp.exe     https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe
# + ffmpeg.exe e ffprobe.exe (ex.: build estático do gyan.dev) em bin/win/

.venv\Scripts\python -m pytest -q          # testes
.venv\Scripts\python -m ig_baixador        # roda a janela

# Build do .exe (rodar da raiz do repo):
.venv\Scripts\pyinstaller build\ig-baixador.spec --noconfirm --distpath dist --workpath build\work
```

O app do **macOS** (`.dmg`) é gerado pelo GitHub Actions (workflow `build-mac.yml`),
num runner macOS — não é possível compilar o app de Mac a partir do Windows.

## Como funciona
Casca em **customtkinter** (interface) por cima de **gallery-dl** (motor principal) com
**yt-dlp** de reserva e **ffmpeg** para juntar áudio+vídeo. A sessão vem só de cookies
(do navegador ou de um `cookies.txt`) — o app **nunca pede usuário/senha**.
