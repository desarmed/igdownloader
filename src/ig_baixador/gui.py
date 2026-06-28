"""Janela Tkinter do IG Baixador."""
from __future__ import annotations

import threading
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .config import load_config, save_config
from .downloader import download

_CONFIG_PATH = Path.home() / ".ig-baixador" / "config.json"


class App:
    def __init__(self, root):
        self.root = root
        self.cfg = load_config(_CONFIG_PATH)
        root.title("IG Baixador")
        root.geometry("620x440")

        ttk.Label(root, text="Link do Instagram (reel, post, story, destaque):").pack(
            anchor="w", padx=12, pady=(12, 2))
        self.url_var = tk.StringVar()
        ttk.Entry(root, textvariable=self.url_var, width=80).pack(
            fill="x", padx=12)

        row = ttk.Frame(root); row.pack(fill="x", padx=12, pady=8)
        self.dest_var = tk.StringVar(value=self.cfg.dest_dir)
        ttk.Label(row, text="Salvar em:").pack(side="left")
        ttk.Entry(row, textvariable=self.dest_var).pack(
            side="left", fill="x", expand=True, padx=6)
        ttk.Button(row, text="Escolher...", command=self._pick_dir).pack(side="left")

        cookie_row = ttk.Frame(root); cookie_row.pack(fill="x", padx=12, pady=(0, 6))
        ttk.Label(cookie_row, text="Cookies do Instagram:").pack(side="left")
        self.cookie_status = ttk.Label(cookie_row, text="")
        self.cookie_status.pack(side="left", padx=6)
        ttk.Button(cookie_row, text="Selecionar cookies.txt...", command=self._pick_cookies).pack(side="left", padx=(6, 2))
        ttk.Button(cookie_row, text="Usar Chrome", command=self._use_chrome).pack(side="left")

        self.btn = ttk.Button(root, text="Baixar", command=self._on_download)
        self.btn.pack(padx=12, pady=4)

        self.status = ttk.Label(root, text="", foreground="#0a7")
        self.status.pack(anchor="w", padx=12)

        self.log = tk.Text(root, height=14, wrap="word")
        self.log.pack(fill="both", expand=True, padx=12, pady=8)

        self._refresh_cookie_status()

    def _refresh_cookie_status(self):
        if (
            self.cfg.cookie_mode == "cookies_txt"
            and self.cfg.cookies_txt_path
            and Path(self.cfg.cookies_txt_path).exists()
        ):
            self.cookie_status.configure(
                text=f"arquivo: {Path(self.cfg.cookies_txt_path).name}"
            )
        else:
            self.cookie_status.configure(text="Chrome (automático)")

    def _pick_cookies(self):
        path = filedialog.askopenfilename(
            title="Selecione o cookies.txt",
            filetypes=[("cookies.txt", "*.txt"), ("Todos", "*.*")],
        )
        if path:
            self.cfg.cookie_mode = "cookies_txt"
            self.cfg.cookies_txt_path = path
            save_config(self.cfg, _CONFIG_PATH)
            self._refresh_cookie_status()
            messagebox.showinfo("Cookies", "Cookies definidos. Agora é só baixar.")

    def _use_chrome(self):
        self.cfg.cookie_mode = "auto"
        self.cfg.cookies_txt_path = ""
        save_config(self.cfg, _CONFIG_PATH)
        self._refresh_cookie_status()

    def _pick_dir(self):
        d = filedialog.askdirectory(initialdir=self.dest_var.get() or ".")
        if d:
            self.dest_var.set(d)

    def _log(self, line):
        self.root.after(0, lambda: (self.log.insert("end", line + "\n"),
                                    self.log.see("end")))

    def _set_status(self, text, ok=True):
        self.root.after(0, lambda: self.status.configure(
            text=text, foreground="#0a7" if ok else "#c33"))

    def _on_download(self):
        url = self.url_var.get().strip()
        if not url:
            self._set_status("Cole um link primeiro.", ok=False)
            return
        self.cfg.dest_dir = self.dest_var.get().strip() or self.cfg.dest_dir
        save_config(self.cfg, _CONFIG_PATH)
        self.btn.configure(state="disabled")
        self._set_status("Baixando...")
        self.log.delete("1.0", "end")
        threading.Thread(target=self._run, args=(url,), daemon=True).start()

    def _prompt_cookies(self):
        answer = messagebox.askyesno(
            "Cookies necessários",
            "Não consegui usar os cookies do Chrome. Exporte um cookies.txt "
            "(extensão 'Get cookies.txt LOCALLY', com a aba do instagram.com aberta) "
            "e selecione o arquivo. Selecionar agora?",
        )
        if answer:
            self._pick_cookies()

    def _run(self, url):
        try:
            res = download(url, self.cfg, on_log=self._log)
            if not res.ok and res.code in ("cookies_locked", "login") and self.cfg.cookie_mode != "cookies_txt":
                self.root.after(0, self._prompt_cookies)
            self._set_status(res.message, ok=res.ok)
        except Exception as e:
            self._log(f"Erro inesperado: {e}")
            self._set_status("Erro inesperado. Veja o log.", ok=False)
        finally:
            self.root.after(0, lambda: self.btn.configure(state="normal"))


def run():
    root = tk.Tk()
    App(root)
    root.mainloop()
