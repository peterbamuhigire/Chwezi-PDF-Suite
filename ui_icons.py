"""Shared icon loading for the Chwezi desktop interfaces."""

from __future__ import annotations

import sys
from pathlib import Path
from tkinter import PhotoImage, TclError
from typing import Any

ICON_ROOT = Path(__file__).resolve().parent / "static" / "icons"


def icon_source(group: str, name: str, suffix: str = ".svg") -> Path:
    """Return a safe path inside the bundled icon directory."""

    if not group.replace("-", "").isalnum() or not name.replace("-", "").isalnum():
        raise ValueError("Icon group and name must use letters, numbers, or hyphens")
    return ICON_ROOT / group / f"{name}{suffix}"


class IconStore:
    """Cache Tk and CustomTkinter images so widgets retain their native resources."""

    def __init__(self) -> None:
        self._tk_images: dict[tuple[str, str, int, str], Any] = {}
        self._ctk_images: dict[tuple[str, str, int], Any] = {}
        self._window_images: dict[str, PhotoImage] = {}

    def tk(self, group: str, name: str, size: int, theme: str) -> Any | None:
        """Return a resized theme-specific PhotoImage, or None in a degraded install."""

        mode = "dark" if theme.casefold() == "dark" else "light"
        key = (group, name, size, mode)
        if key in self._tk_images:
            return self._tk_images[key]
        path = ICON_ROOT / "raster" / mode / group / f"{name}.png"
        if not path.is_file():
            return None
        try:
            from PIL import Image, ImageTk

            with Image.open(path) as source:
                image = source.convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
        except (ImportError, OSError):
            return None
        self._tk_images[key] = photo
        return photo

    def ctk(self, group: str, name: str, size: int) -> Any | None:
        """Return a light/dark CTkImage, or None when desktop image support is unavailable."""

        key = (group, name, size)
        if key in self._ctk_images:
            return self._ctk_images[key]
        light_path = ICON_ROOT / "raster" / "light" / group / f"{name}.png"
        dark_path = ICON_ROOT / "raster" / "dark" / group / f"{name}.png"
        if not light_path.is_file() or not dark_path.is_file():
            return None
        try:
            import customtkinter as ctk
            from PIL import Image

            with Image.open(light_path) as source:
                light = source.convert("RGBA")
            with Image.open(dark_path) as source:
                dark = source.convert("RGBA")
            image = ctk.CTkImage(light_image=light, dark_image=dark, size=(size, size))
        except (ImportError, OSError):
            return None
        self._ctk_images[key] = image
        return image

    def apply_window_icon(self, root: Any, app_name: str) -> bool:
        """Apply a distinct window/taskbar icon without preventing application startup."""

        ico_path = icon_source("apps", app_name, ".ico")
        light_png = ICON_ROOT / "raster" / "light" / "apps" / f"{app_name}.png"
        try:
            if sys.platform == "win32" and ico_path.is_file():
                root.iconbitmap(default=str(ico_path))
                return True
            if light_png.is_file():
                photo = PhotoImage(file=str(light_png))
                self._window_images[app_name] = photo
                root.iconphoto(True, photo)
                return True
        except (OSError, RuntimeError, TclError):
            return False
        return False
