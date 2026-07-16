#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chwezi Document Suite central launcher."""

import subprocess
import sys
import threading
import webbrowser
import time
from pathlib import Path

import customtkinter as ctk

from window_geometry import centered_geometry

HERE = Path(__file__).parent

# ── Appearance ────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# ── Colour palette ────────────────────────────────────────────────────────────
BG_MAIN   = "#1a1a2e"
BG_CARD   = "#16213e"
BG_HOVER  = "#0f3460"
ACCENT    = "#e94560"
TEXT_PRI  = "#eaeaea"
TEXT_SEC  = "#8892a4"
GREEN     = "#4caf50"
GRAY      = "#555f6e"

TOOLS = [
    {
        "id":          "web",
        "title":       "PDF Organizer",
        "description": "AI-powered PDF categorization\nwith batch processing",
        "icon":        "📂",
        "script":      "web_interface.py",
        "url":         "http://localhost:5000",
        "terminal":    False,
    },
    {
        "id":          "sign",
        "title":       "PDF Signer",
        "description": "Add PNG signatures to PDFs\nwith full layout control",
        "icon":        "✍",
        "script":      "sign_setup.py",
        "terminal":    True,
    },
    {
        "id":          "documents_markdown",
        "title":       "Documents to Markdown",
        "description": "Convert PDF, Word, EPUB, and PPTX\ninto structured Markdown files",
        "icon":        "📘",
        "script":      "documents_to_markdown.py",
        "args":        ["--gui"],
        "terminal":    False,
    },
]


class ToolCard(ctk.CTkFrame):
    """One card per tool with live status badge and launch/stop controls."""

    def __init__(self, master, tool: dict, **kwargs):
        super().__init__(master, corner_radius=16, fg_color=BG_CARD, **kwargs)
        self.tool = tool
        self.process: subprocess.Popen | None = None
        self._monitor_thread: threading.Thread | None = None

        self._build()
        self._update_status(running=False)

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build(self):
        self.columnconfigure(0, weight=1)

        # Icon
        ctk.CTkLabel(
            self, text=self.tool["icon"],
            font=ctk.CTkFont(size=48),
            text_color=TEXT_PRI,
        ).grid(row=0, column=0, pady=(22, 4))

        # Title
        ctk.CTkLabel(
            self, text=self.tool["title"],
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT_PRI,
        ).grid(row=1, column=0, padx=20)

        # Description
        ctk.CTkLabel(
            self, text=self.tool["description"],
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SEC,
            justify="center",
        ).grid(row=2, column=0, padx=20, pady=(4, 14))

        # Status badge
        self.status_badge = ctk.CTkLabel(
            self, text="",
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=8,
            width=90, height=22,
        )
        self.status_badge.grid(row=3, column=0, pady=(0, 12))

        # Launch button
        self.launch_btn = ctk.CTkButton(
            self, text="Launch",
            width=140, height=38,
            corner_radius=10,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color=ACCENT, hover_color="#c73652",
            command=self._on_launch,
        )
        self.launch_btn.grid(row=4, column=0, pady=(0, 22))

    # ── State helpers ─────────────────────────────────────────────────────────

    def _update_status(self, running: bool):
        if running:
            self.status_badge.configure(
                text="● Running",
                text_color=GREEN,
                fg_color="#1e3a1e",
            )
            self.launch_btn.configure(text="Open", fg_color="#1565c0", hover_color="#0d47a1")
        else:
            self.status_badge.configure(
                text="○ Stopped",
                text_color=GRAY,
                fg_color="#2a2a2a",
            )
            self.launch_btn.configure(text="Launch", fg_color=ACCENT, hover_color="#c73652")

    def _is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    # ── Actions ───────────────────────────────────────────────────────────────

    def _on_launch(self):
        if self._is_running():
            self._bring_to_front()
            return
        self._launch()

    def _launch(self):
        script = HERE / self.tool["script"]
        args = self.tool.get("args", [])

        if self.tool.get("terminal"):
            self._launch_terminal(script)
        else:
            cmd = [sys.executable, str(script)] + args
            self.process = subprocess.Popen(
                cmd,
                cwd=str(HERE),
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )

        self._update_status(running=True)
        self._start_monitor()

        url = self.tool.get("url")
        if url:
            threading.Thread(target=self._open_url_delayed, args=(url,), daemon=True).start()

    def _launch_terminal(self, script: Path):
        title = self.tool["title"]
        py = sys.executable
        if sys.platform == "win32":
            self.process = subprocess.Popen(
                f'start "{title}" cmd /k ""{py}" "{script}""',
                shell=True,
                cwd=str(HERE),
            )
        elif sys.platform == "darwin":
            self.process = subprocess.Popen(
                ["osascript", "-e",
                 f'tell application "Terminal" to do script "cd {HERE} && {py} {script}"'],
                cwd=str(HERE),
            )
        else:
            for term in ("x-terminal-emulator", "gnome-terminal", "xterm"):
                if subprocess.run(["which", term], capture_output=True).returncode == 0:
                    self.process = subprocess.Popen(
                        [term, "-e", f"{py} {script}"],
                        cwd=str(HERE),
                    )
                    break

    def _open_url_delayed(self, url: str, delay: float = 2.5):
        time.sleep(delay)
        webbrowser.open(url)

    def _bring_to_front(self):
        url = self.tool.get("url")
        if url:
            webbrowser.open(url)

    def _start_monitor(self):
        self._monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        self._monitor_thread.start()

    def _monitor(self):
        """Poll process until it exits, then update UI on the main thread."""
        while self._is_running():
            time.sleep(1)
        self.after(0, self._update_status, False)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.title("Chwezi Document Suite")
        self.resizable(False, False)
        self._build()
        self.update_idletasks()
        self._center()
        self.deiconify()

    def _build(self):
        self.configure(fg_color=BG_MAIN)

        # ── Header ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(28, 0))

        ctk.CTkLabel(
            header,
            text="Chwezi Document Suite",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color=TEXT_PRI,
        ).pack(side="left")

        self.theme_btn = ctk.CTkButton(
            header,
            text="☀ Light",
            width=90, height=30,
            corner_radius=8,
            font=ctk.CTkFont(size=12),
            fg_color="#2a2a4a", hover_color=BG_HOVER,
            command=self._toggle_theme,
        )
        self.theme_btn.pack(side="right")

        # ── Subtitle ──────────────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="Select a tool to launch",
            font=ctk.CTkFont(size=13),
            text_color=TEXT_SEC,
        ).pack(padx=30, pady=(6, 20))

        # ── Tool cards ────────────────────────────────────────────────────────
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.pack(padx=30, pady=(0, 28))

        for col, tool in enumerate(TOOLS):
            card = ToolCard(cards_frame, tool, width=200)
            card.grid(row=0, column=col, padx=8, pady=0, sticky="nsew")
            cards_frame.columnconfigure(col, weight=1)

        # ── Footer ────────────────────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="Chwezi Document Suite  •  All tools run locally",
            font=ctk.CTkFont(size=10),
            text_color=GRAY,
        ).pack(pady=(0, 16))

    def _center(self):
        width = max(self.winfo_reqwidth(), self.winfo_width())
        height = max(self.winfo_reqheight(), self.winfo_height())
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(centered_geometry(width, height, screen_width, screen_height))

    def _toggle_theme(self):
        current = ctk.get_appearance_mode()
        if current == "Dark":
            ctk.set_appearance_mode("light")
            self.theme_btn.configure(text="🌙 Dark")
        else:
            ctk.set_appearance_mode("dark")
            self.theme_btn.configure(text="☀ Light")


if __name__ == "__main__":
    app = App()
    app.mainloop()
