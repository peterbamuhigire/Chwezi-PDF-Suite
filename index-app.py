#!/usr/bin/env python3
"""Chwezi Document Suite launcher for source and frozen installations."""

from __future__ import annotations

import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

from ui_icons import IconStore
from ui_theme import BODY_FONT, DISPLAY_FONT, colour, load_theme, save_theme
from window_geometry import centered_geometry

SOURCE_DIR = Path(__file__).resolve().parent
INITIAL_THEME = load_theme()
ctk.set_appearance_mode(INITIAL_THEME)
ctk.set_default_color_theme("blue")

TOOLS = [
    {
        "id": "organizer",
        "code": "ORG",
        "icon": "app-pdf-organizer",
        "eyebrow": "LIBRARY WORKFLOW",
        "title": "PDF Organizer",
        "description": (
            "Review, categorize, and move PDF collections in the dedicated batch organizer."
        ),
        "script": "organize_batch.py",
        "executable": "ChweziOrganizer",
        "args": [],
    },
    {
        "id": "signer",
        "code": "SIGN",
        "icon": "app-pdf-signer",
        "eyebrow": "PDF FINISHING",
        "title": "PDF Signer",
        "description": (
            "Place a PNG signature with precise page, position, scale, and opacity controls."
        ),
        "script": "pdf_signature.py",
        "executable": "ChweziSigner",
        "args": [],
    },
    {
        "id": "converter",
        "code": "MD",
        "icon": "app-documents-to-markdown",
        "eyebrow": "CONTENT EXTRACTION",
        "title": "Documents to Markdown",
        "description": "Turn PDF, Word, EPUB, and PowerPoint files into structured Markdown.",
        "script": "documents_to_markdown.py",
        "executable": "ChweziMarkdown",
        "args": ["--gui"],
    },
]


def is_frozen() -> bool:
    return bool(getattr(sys, "frozen", False))


def installed_directory() -> Path:
    """Return the folder containing installed sibling executables."""

    if is_frozen():
        return Path(sys.executable).resolve().parent
    return SOURCE_DIR


def command_for(tool: dict[str, object]) -> list[str]:
    args = [str(value) for value in tool.get("args", [])]
    if is_frozen():
        suffix = ".exe" if sys.platform == "win32" else ""
        target = installed_directory() / f"{tool['executable']}{suffix}"
        return [str(target), *args]
    return [sys.executable, str(SOURCE_DIR / str(tool["script"])), *args]


class ToolCard(ctk.CTkFrame):
    """A themed suite card with process-aware launch state."""

    def __init__(self, master, tool: dict[str, object], icons: IconStore, **kwargs):
        super().__init__(
            master,
            corner_radius=18,
            fg_color=colour("surface_raised"),
            border_width=1,
            border_color=colour("border"),
            **kwargs,
        )
        self.tool = tool
        self.icons = icons
        self.process: subprocess.Popen | None = None
        self._build()
        self._update_status(False)

    def _build(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
        top.grid_columnconfigure(1, weight=1)

        tool_icon = self.icons.ctk("apps", str(self.tool["icon"]), 34)
        ctk.CTkLabel(
            top,
            text="" if tool_icon else str(self.tool["code"]),
            image=tool_icon,
            width=52,
            height=36,
            corner_radius=10,
            fg_color=colour("accent_soft"),
            text_color=colour("accent"),
            font=ctk.CTkFont(family=BODY_FONT, size=11, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            top,
            text=str(self.tool["eyebrow"]),
            text_color=colour("text_muted"),
            font=ctk.CTkFont(family=BODY_FONT, size=10, weight="bold"),
        ).grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            self,
            text=str(self.tool["title"]),
            anchor="w",
            text_color=colour("text_primary"),
            font=ctk.CTkFont(family=DISPLAY_FONT, size=20, weight="bold"),
        ).grid(row=1, column=0, sticky="ew", padx=20, pady=(22, 6))

        ctk.CTkLabel(
            self,
            text=str(self.tool["description"]),
            anchor="nw",
            justify="left",
            wraplength=205,
            text_color=colour("text_muted"),
            font=ctk.CTkFont(family=BODY_FONT, size=12),
        ).grid(row=2, column=0, sticky="new", padx=20)

        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=4, column=0, sticky="ew", padx=20, pady=(22, 20))
        footer.grid_columnconfigure(0, weight=1)

        self.status_badge = ctk.CTkLabel(
            footer,
            text="",
            height=30,
            corner_radius=9,
            font=ctk.CTkFont(family=BODY_FONT, size=10, weight="bold"),
        )
        self.status_badge.grid(row=0, column=0, sticky="w")

        self.launch_btn = ctk.CTkButton(
            footer,
            text="Open tool",
            image=self.icons.ctk("navigation", "arrow-right", 15),
            compound="right",
            width=104,
            height=38,
            corner_radius=10,
            fg_color=colour("accent"),
            hover_color=colour("accent_hover"),
            text_color=colour("accent_text"),
            font=ctk.CTkFont(family=BODY_FONT, size=11, weight="bold"),
            command=self._on_launch,
        )
        self.launch_btn.grid(row=0, column=1, sticky="e")

    def _update_status(self, running: bool) -> None:
        if running:
            self.status_badge.configure(
                text="  RUNNING  ",
                image=self.icons.ctk("status", "circle-play", 13),
                compound="left",
                text_color=colour("success"),
                fg_color=colour("success_soft"),
            )
            self.launch_btn.configure(text="Open again" if self.tool.get("url") else "Running")
        else:
            self.status_badge.configure(
                text="  READY  ",
                image=self.icons.ctk("status", "circle-check", 13),
                compound="left",
                text_color=colour("text_muted"),
                fg_color=colour("surface_sunken"),
            )
            self.launch_btn.configure(text="Open tool", state="normal")

    def _is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def _on_launch(self) -> None:
        if self._is_running():
            url = self.tool.get("url")
            if url:
                webbrowser.open(str(url))
            return
        self._launch()

    def _launch(self) -> None:
        command = command_for(self.tool)
        target = Path(command[0])
        if is_frozen() and not target.is_file():
            messagebox.showerror(
                "Tool not installed",
                f"The installed tool is missing:\n\n{target}\n\nReinstall the suite to repair it.",
            )
            return
        try:
            self.process = subprocess.Popen(  # noqa: S603 - command targets declared suite apps.
                command,
                cwd=str(installed_directory()),
                shell=False,
                creationflags=(subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0),
            )
        except OSError as exc:
            messagebox.showerror(
                "Could not open tool",
                f"{self.tool['title']} could not start.\n\n{exc}",
            )
            return

        self._update_status(True)
        if not self.tool.get("url"):
            self.launch_btn.configure(state="disabled")
        threading.Thread(target=self._monitor, daemon=True).start()
        url = self.tool.get("url")
        if url:
            threading.Thread(target=self._open_when_ready, args=(str(url),), daemon=True).start()

    def _open_when_ready(self, url: str) -> None:
        if not url.startswith("http://127.0.0.1:"):
            return
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline and self._is_running():
            try:
                with urllib.request.urlopen(url, timeout=0.8):  # noqa: S310 - localhost only.
                    webbrowser.open(url)
                    return
            except (urllib.error.URLError, TimeoutError, OSError):
                time.sleep(0.35)

    def _monitor(self) -> None:
        while self._is_running():
            time.sleep(0.8)
        self.after(0, self._update_status, False)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.icons = IconStore()
        self.icons.apply_window_icon(self, "app-chwezi-document-suite")
        self.withdraw()
        self.title("Chwezi Document Suite")
        self.resizable(False, False)
        self._build()
        self.update_idletasks()
        self._center()
        self.after_idle(self._show)

    def _build(self) -> None:
        self.configure(fg_color=colour("surface_base"))
        shell = ctk.CTkFrame(self, fg_color="transparent")
        shell.pack(fill="both", expand=True, padx=34, pady=30)

        header = ctk.CTkFrame(shell, fg_color="transparent")
        header.pack(fill="x")
        ctk.CTkLabel(
            header,
            text="PRIVATE · LOCAL · MODULAR",
            text_color=colour("accent"),
            font=ctk.CTkFont(family=BODY_FONT, size=10, weight="bold"),
        ).pack(anchor="w")

        title_row = ctk.CTkFrame(header, fg_color="transparent")
        title_row.pack(fill="x", pady=(7, 0))
        ctk.CTkLabel(
            title_row,
            text="",
            image=self.icons.ctk("apps", "app-chwezi-document-suite", 38),
        ).pack(side="left", padx=(0, 12))
        ctk.CTkLabel(
            title_row,
            text="Chwezi Document Suite",
            text_color=colour("text_primary"),
            font=ctk.CTkFont(family=DISPLAY_FONT, size=30, weight="bold"),
        ).pack(side="left")
        self.theme_btn = ctk.CTkButton(
            title_row,
            text="",
            width=110,
            height=36,
            corner_radius=10,
            fg_color=colour("surface_raised"),
            hover_color=colour("surface_hover"),
            border_width=1,
            border_color=colour("border"),
            text_color=colour("text_primary"),
            font=ctk.CTkFont(family=BODY_FONT, size=11, weight="bold"),
            command=self._toggle_theme,
        )
        self.theme_btn.pack(side="right")
        self._sync_theme_button()

        ctk.CTkLabel(
            header,
            text="One calm workspace for organizing, signing, and extracting documents.",
            text_color=colour("text_muted"),
            font=ctk.CTkFont(family=BODY_FONT, size=13),
        ).pack(anchor="w", pady=(7, 0))

        rule = ctk.CTkFrame(shell, height=1, fg_color=colour("border"))
        rule.pack(fill="x", pady=(24, 22))

        cards = ctk.CTkFrame(shell, fg_color="transparent")
        cards.pack(fill="x")
        for column, tool in enumerate(TOOLS):
            cards.grid_columnconfigure(column, weight=1, uniform="tools")
            ToolCard(cards, tool, icons=self.icons, width=245, height=300).grid(
                row=0,
                column=column,
                padx=(0 if column == 0 else 8, 0 if column == 2 else 8),
                sticky="nsew",
            )

        footer = ctk.CTkFrame(shell, fg_color="transparent")
        footer.pack(fill="x", pady=(20, 0))
        ctk.CTkLabel(
            footer,
            text="Files stay on this computer unless you explicitly use an AI provider.",
            text_color=colour("text_muted"),
            font=ctk.CTkFont(family=BODY_FONT, size=10),
        ).pack(side="left")
        ctk.CTkLabel(
            footer,
            text="SUITE 0.2",
            text_color=colour("text_muted"),
            font=ctk.CTkFont(family=BODY_FONT, size=9, weight="bold"),
        ).pack(side="right")

    def _center(self) -> None:
        width = max(self.winfo_reqwidth(), self.winfo_width())
        height = max(self.winfo_reqheight(), self.winfo_height())
        self.geometry(
            centered_geometry(
                width,
                height,
                self.winfo_screenwidth(),
                self.winfo_screenheight(),
            )
        )

    def _show(self) -> None:
        self.deiconify()
        self.lift()
        self.attributes("-topmost", True)
        self.focus_force()
        self.after(250, lambda: self.attributes("-topmost", False))

    def _sync_theme_button(self) -> None:
        mode = ctk.get_appearance_mode().casefold()
        icon_name = "sun" if mode == "dark" else "moon"
        self.theme_btn.configure(
            text="Light mode" if mode == "dark" else "Dark mode",
            image=self.icons.ctk("navigation", icon_name, 15),
            compound="left",
        )

    def _toggle_theme(self) -> None:
        next_mode = "light" if ctk.get_appearance_mode() == "Dark" else "dark"
        ctk.set_appearance_mode(next_mode)
        save_theme(next_mode)
        self._sync_theme_button()


if __name__ == "__main__":
    App().mainloop()
