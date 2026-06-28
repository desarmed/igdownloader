"""Construção de comandos, classificação de erro e orquestração do download."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass

from .binaries import resolve_binary
from .cookies import cookie_args
from .urls import is_instagram_url, normalize_url, detect_url_type


def build_gallery_dl_cmd(bin_path, url, dest_dir, cookie):
    return [bin_path, *cookie, "-d", dest_dir, url]


def build_ytdlp_cmd(bin_path, url, dest_dir, cookie):
    return [
        bin_path, *cookie,
        "-P", dest_dir,
        "-o", "%(uploader_id)s/%(id)s.%(ext)s",
        url,
    ]


def classify_error(stdout, stderr, returncode):
    if returncode == 0:
        return ("ok", "Download concluído.")
    blob = (stdout + "\n" + stderr).lower()
    if "401" in blob or "login required" in blob or "challenge" in blob:
        return ("login", "Faça login no Instagram pelo Chrome e tente de novo.")
    if ("dpapi" in blob or "could not copy" in blob or "unable to read" in blob
            or "failed to decrypt" in blob
            or ("permission denied" in blob and "cookies" in blob)):
        return ("cookies_locked",
                "Não consegui ler os cookies do Chrome. Feche o Chrome e tente de novo, "
                "ou use o cookies.txt.")
    if "429" in blob or "too many requests" in blob or "please wait" in blob:
        return ("rate_limit", "O Instagram pediu pra esperar. Tente de novo em alguns minutos.")
    if "not available" in blob or "private" in blob or "404" in blob:
        return ("private", "Conteúdo privado ou indisponível.")
    return ("unknown", "Falhou. Veja o log de detalhes abaixo.")


@dataclass
class DownloadResult:
    ok: bool
    code: str
    message: str
    log: str


def _default_runner(cmd):
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    return (proc.returncode, proc.stdout, proc.stderr)


def download(url, cfg, on_log=None, runner=None):
    runner = runner or _default_runner
    log_lines = []

    def emit(line):
        log_lines.append(line)
        if on_log:
            on_log(line)

    if not is_instagram_url(url):
        msg = "Esse link não é do Instagram."
        emit(msg)
        return DownloadResult(False, "not_instagram", msg, "\n".join(log_lines))

    url = normalize_url(url)
    ck = cookie_args(cfg)

    # 1) gallery-dl (principal)
    emit("Baixando com gallery-dl...")
    try:
        gd = str(resolve_binary("gallery-dl"))
        rc, out, err = runner(build_gallery_dl_cmd(gd, url, cfg.dest_dir, ck))
    except Exception:
        return DownloadResult(False, "unknown",
                              "Não encontrei o programa de download embutido. Reinstale o app.",
                              "\n".join(log_lines))
    if out: emit(out)
    if err: emit(err)
    code, message = classify_error(out, err, rc)
    if code == "ok":
        return DownloadResult(True, code, message, "\n".join(log_lines))

    # 2) fallback yt-dlp só pra vídeo (reel/post)
    if detect_url_type(url) in ("reel", "post"):
        emit("Tentando de novo com yt-dlp...")
        try:
            yt = str(resolve_binary("yt-dlp"))
            rc2, out2, err2 = runner(build_ytdlp_cmd(yt, url, cfg.dest_dir, ck))
        except Exception:
            return DownloadResult(False, "unknown",
                                  "Não encontrei o programa de download embutido. Reinstale o app.",
                                  "\n".join(log_lines))
        if out2: emit(out2)
        if err2: emit(err2)
        code2, message2 = classify_error(out2, err2, rc2)
        if code2 == "ok":
            return DownloadResult(True, code2, message2, "\n".join(log_lines))
        return DownloadResult(False, code2, message2, "\n".join(log_lines))

    return DownloadResult(False, code, message, "\n".join(log_lines))
