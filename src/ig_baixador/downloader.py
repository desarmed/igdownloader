"""Construção de comandos, classificação de erro e orquestração do download."""
from __future__ import annotations


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
    if "dpapi" in blob or "could not copy" in blob or "unable to read" in blob \
            or "failed to decrypt" in blob or "permission denied" in blob and "cookies" in blob:
        return ("cookies_locked",
                "Não consegui ler os cookies do Chrome. Feche o Chrome e tente de novo, "
                "ou use o cookies.txt.")
    if "429" in blob or "too many requests" in blob or "please wait" in blob:
        return ("rate_limit", "O Instagram pediu pra esperar. Tente de novo em alguns minutos.")
    if "not available" in blob or "private" in blob or "404" in blob:
        return ("private", "Conteúdo privado ou indisponível.")
    return ("unknown", "Falhou. Veja o log de detalhes abaixo.")
