"""Janela customtkinter do IG Baixador — Mesa de Captura / Plum-Ember."""
from __future__ import annotations

import threading
from pathlib import Path
from tkinter import filedialog, messagebox
from urllib.parse import urlparse

import customtkinter as ctk

from .config import load_config, save_config
from .downloader import download
from .urls import parse_links, detect_url_type

_CONFIG_PATH = Path.home() / ".ig-baixador" / "config.json"

# ── Design tokens ────────────────────────────────────────────────────────────
BG          = "#15131C"
CARD        = "#2C2838"
SURFACE_ALT = "#211E2B"
TEXT        = "#F2EEF7"
MUTED       = "#9A92A8"
ACCENT      = "#FF6A3D"
ACCENT_HOV  = "#E85A30"
SUCCESS     = "#43D9A3"
ERROR       = "#FF5C7A"


def _short_label(url: str) -> str:
    """Gera um rótulo curto para a URL: tipo + shortcode."""
    kind = detect_url_type(url)
    parts = [p for p in urlparse(url).path.split("/") if p]
    shortcode = parts[-1] if parts else url[:30]
    if kind == "unknown":
        return url[:40] if len(url) > 40 else url
    return f"{kind} / {shortcode}"


class _QueueRow(ctk.CTkFrame):
    """Uma linha na fila de downloads."""

    def __init__(self, master, url: str, **kwargs):
        super().__init__(master, fg_color=SURFACE_ALT, corner_radius=8, **kwargs)
        self.url = url

        self.columnconfigure(1, weight=1)

        self._label = ctk.CTkLabel(
            self, text=_short_label(url), text_color=MUTED,
            font=ctk.CTkFont(size=12), anchor="w",
        )
        self._label.grid(row=0, column=0, padx=(10, 6), pady=6, sticky="w")

        self._bar = ctk.CTkProgressBar(
            self, width=180, height=8,
            fg_color=CARD, progress_color=ACCENT,
            mode="indeterminate",
        )
        self._bar.set(0)
        self._bar.grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        self._status = ctk.CTkLabel(
            self, text="na fila", text_color=MUTED,
            font=ctk.CTkFont(size=11), width=90, anchor="e",
        )
        self._status.grid(row=0, column=2, padx=(6, 10), pady=6, sticky="e")

    def set_downloading(self):
        self._status.configure(text="baixando…", text_color=TEXT)
        self._bar.configure(mode="indeterminate", progress_color=ACCENT)
        self._bar.start()

    def set_done(self):
        self._bar.stop()
        self._bar.configure(mode="determinate", progress_color=SUCCESS)
        self._bar.set(1.0)
        self._status.configure(text="✓ concluído", text_color=SUCCESS)
        self._label.configure(text_color=TEXT)

    def set_error(self, msg: str):
        self._bar.stop()
        self._bar.configure(mode="determinate", progress_color=ERROR)
        self._bar.set(0)
        short = msg[:35] + "…" if len(msg) > 35 else msg
        self._status.configure(text=f"✕ {short}", text_color=ERROR)
        self._label.configure(text_color=MUTED)


class App:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.cfg = load_config(_CONFIG_PATH)

        root.title("IG Baixador")
        root.geometry("760x640")
        root.resizable(True, True)
        root.configure(fg_color=BG)

        self._build_ui()
        self._refresh_cookie_pill()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        root = self.root
        root.columnconfigure(0, weight=1)
        root.rowconfigure(5, weight=1)  # queue frame expands

        # 1. Header
        header = ctk.CTkFrame(root, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 8))
        header.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header, text="IG Baixador",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT,
        ).grid(row=0, column=0, sticky="w")

        self._pill = ctk.CTkButton(
            header, text="cookies: Chrome",
            font=ctk.CTkFont(size=11),
            fg_color=CARD, hover_color=SURFACE_ALT,
            text_color=MUTED, corner_radius=20,
            width=150, height=28,
            command=self._pick_cookies,
        )
        self._pill.grid(row=0, column=2, sticky="e")

        # 2. Links textbox
        ctk.CTkLabel(
            root, text="Cole os links (um por linha)",
            font=ctk.CTkFont(size=12), text_color=MUTED, anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(0, 4))

        self._links_box = ctk.CTkTextbox(
            root, height=110,
            fg_color=CARD, text_color=TEXT,
            border_color=SURFACE_ALT, border_width=1,
            corner_radius=12, font=ctk.CTkFont(size=13),
        )
        self._links_box.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))

        # 3. Destination row
        dest_row = ctk.CTkFrame(root, fg_color="transparent")
        dest_row.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 6))
        dest_row.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            dest_row, text="Salvar em:",
            font=ctk.CTkFont(size=12), text_color=MUTED,
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))

        self._dest_var = ctk.StringVar(value=self.cfg.dest_dir)
        ctk.CTkEntry(
            dest_row, textvariable=self._dest_var,
            fg_color=CARD, text_color=TEXT, border_color=SURFACE_ALT,
            corner_radius=8, font=ctk.CTkFont(size=13),
        ).grid(row=0, column=1, sticky="ew", padx=(0, 8))

        ctk.CTkButton(
            dest_row, text="Escolher…",
            fg_color=CARD, hover_color=SURFACE_ALT,
            text_color=TEXT, corner_radius=8, width=90,
            command=self._pick_dir,
        ).grid(row=0, column=2)

        # 4. Cookies row
        ck_row = ctk.CTkFrame(root, fg_color="transparent")
        ck_row.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 10))

        ctk.CTkLabel(
            ck_row, text="Cookies do Instagram:",
            font=ctk.CTkFont(size=12), text_color=MUTED,
        ).pack(side="left")

        self._cookie_status_lbl = ctk.CTkLabel(
            ck_row, text="", font=ctk.CTkFont(size=12), text_color=MUTED,
        )
        self._cookie_status_lbl.pack(side="left", padx=8)

        ctk.CTkButton(
            ck_row, text="Selecionar cookies.txt…",
            fg_color=CARD, hover_color=SURFACE_ALT,
            text_color=TEXT, corner_radius=8, height=28,
            command=self._pick_cookies,
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            ck_row, text="Usar Chrome",
            fg_color=CARD, hover_color=SURFACE_ALT,
            text_color=MUTED, corner_radius=8, height=28,
            command=self._use_chrome,
        ).pack(side="left")

        # 5. Primary button
        self._btn = ctk.CTkButton(
            root, text="Baixar tudo",
            fg_color=ACCENT, hover_color=ACCENT_HOV,
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=8, height=40,
            command=self._on_download,
        )
        self._btn.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 10))

        # 6. Queue section
        ctk.CTkLabel(
            root, text="Fila",
            font=ctk.CTkFont(size=12), text_color=MUTED, anchor="w",
        ).grid(row=6, column=0, sticky="w", padx=20, pady=(0, 4))

        self._queue_frame = ctk.CTkScrollableFrame(
            root, fg_color=CARD, corner_radius=12,
        )
        self._queue_frame.grid(row=7, column=0, sticky="nsew", padx=20, pady=(0, 16))
        self._queue_frame.columnconfigure(0, weight=1)
        root.rowconfigure(7, weight=1)

        self._rows: list[_QueueRow] = []

    # ── Cookie helpers ────────────────────────────────────────────────────────

    def _refresh_cookie_pill(self):
        if (
            self.cfg.cookie_mode == "cookies_txt"
            and self.cfg.cookies_txt_path
            and Path(self.cfg.cookies_txt_path).exists()
        ):
            self._pill.configure(
                text="cookies: arquivo", text_color=SUCCESS,
            )
            self._cookie_status_lbl.configure(
                text=Path(self.cfg.cookies_txt_path).name, text_color=SUCCESS,
            )
        else:
            self._pill.configure(text="cookies: Chrome", text_color=MUTED)
            self._cookie_status_lbl.configure(text="Chrome (automático)", text_color=MUTED)

    def _pick_cookies(self):
        path = filedialog.askopenfilename(
            title="Selecione o cookies.txt",
            filetypes=[("cookies.txt", "*.txt"), ("Todos", "*.*")],
        )
        if path:
            self.cfg.cookie_mode = "cookies_txt"
            self.cfg.cookies_txt_path = path
            save_config(self.cfg, _CONFIG_PATH)
            self._refresh_cookie_pill()
            messagebox.showinfo("Cookies", "Cookies definidos. Agora é só baixar.")

    def _use_chrome(self):
        self.cfg.cookie_mode = "auto"
        self.cfg.cookies_txt_path = ""
        save_config(self.cfg, _CONFIG_PATH)
        self._refresh_cookie_pill()

    def _pick_dir(self):
        d = filedialog.askdirectory(initialdir=self._dest_var.get() or ".")
        if d:
            self._dest_var.set(d)

    # ── Download orchestration ────────────────────────────────────────────────

    def _on_download(self):
        raw = self._links_box.get("1.0", "end")
        links = parse_links(raw)
        if not links:
            messagebox.showwarning("Sem links", "Cole pelo menos um link.")
            return

        # Save config
        self.cfg.dest_dir = self._dest_var.get().strip() or self.cfg.dest_dir
        save_config(self.cfg, _CONFIG_PATH)

        # Disable button
        self._btn.configure(state="disabled", fg_color=SURFACE_ALT, text_color=MUTED)

        # Clear and rebuild queue
        for w in self._queue_frame.winfo_children():
            w.destroy()
        self._rows = []
        for url in links:
            row = _QueueRow(self._queue_frame, url)
            row.grid(sticky="ew", pady=(0, 4))
            self._queue_frame.columnconfigure(0, weight=1)
            self._rows.append(row)

        # Start background worker
        threading.Thread(
            target=self._worker, args=(links,), daemon=True,
        ).start()

    def _worker(self, links: list[str]):
        failed_codes: list[str] = []
        try:
            for i, url in enumerate(links):
                row = self._rows[i]
                self.root.after(0, row.set_downloading)
                try:
                    res = download(url, self.cfg)
                    if res.ok:
                        self.root.after(0, row.set_done)
                    else:
                        failed_codes.append(res.code)
                        msg = res.message
                        self.root.after(0, lambda r=row, m=msg: r.set_error(m))
                except Exception as e:
                    failed_codes.append("unknown")
                    err_msg = str(e)
                    self.root.after(0, lambda r=row, m=err_msg: r.set_error(m))
        except Exception:
            pass
        finally:
            self.root.after(0, self._on_worker_done)
            # Prompt cookies if needed
            needs_cookies = any(c in ("cookies_locked", "login") for c in failed_codes)
            if needs_cookies and self.cfg.cookie_mode != "cookies_txt":
                self.root.after(0, self._prompt_cookies)

    def _on_worker_done(self):
        self._btn.configure(state="normal", fg_color=ACCENT, text_color="#FFFFFF")

    def _prompt_cookies(self):
        answer = messagebox.askyesno(
            "Cookies necessários",
            "Não consegui usar os cookies do Chrome. Exporte um cookies.txt "
            "(extensão 'Get cookies.txt LOCALLY', aba do instagram.com) "
            "e selecione o arquivo. Selecionar agora?",
        )
        if answer:
            self._pick_cookies()


def run():
    ctk.set_appearance_mode("dark")
    root = ctk.CTk()
    App(root)
    root.mainloop()
