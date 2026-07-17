"""Shared visual tokens and theme helpers for the Chwezi desktop tools."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from tkinter import ttk

DISPLAY_FONT = "Georgia"
BODY_FONT = "Trebuchet MS"
MONO_FONT = "Cascadia Mono"


@dataclass(frozen=True)
class Palette:
    """Semantic colours for one appearance mode."""

    surface_base: str
    surface_raised: str
    surface_sunken: str
    surface_hover: str
    text_primary: str
    text_muted: str
    border: str
    accent: str
    accent_hover: str
    accent_text: str
    accent_soft: str
    accent_secondary: str
    success: str
    success_soft: str
    warning: str
    danger: str
    focus: str


LIGHT = Palette(
    surface_base="#F5F1E8",
    surface_raised="#FFFDF7",
    surface_sunken="#EAE4D7",
    surface_hover="#E3EEE9",
    text_primary="#17252B",
    text_muted="#53666B",
    border="#B8C4BF",
    accent="#006C67",
    accent_hover="#00524F",
    accent_text="#FFFDF7",
    accent_soft="#D6EEEA",
    accent_secondary="#B8444F",
    success="#217A55",
    success_soft="#DCEFE4",
    warning="#825500",
    danger="#B53A43",
    focus="#0A7E78",
)

DARK = Palette(
    surface_base="#101D22",
    surface_raised="#17282E",
    surface_sunken="#0C171B",
    surface_hover="#20383F",
    text_primary="#E8EEE9",
    text_muted="#A9BBB9",
    border="#466169",
    accent="#69C8BD",
    accent_hover="#89D8CE",
    accent_text="#09211F",
    accent_soft="#203E3D",
    accent_secondary="#FF8A88",
    success="#74C69D",
    success_soft="#193B31",
    warning="#F0BF63",
    danger="#FF8A88",
    focus="#8ADBD1",
)


def colour(role: str) -> tuple[str, str]:
    """Return a CustomTkinter-compatible (light, dark) semantic colour pair."""

    return getattr(LIGHT, role), getattr(DARK, role)


def palette_for(mode: str) -> Palette:
    return LIGHT if mode.casefold() == "light" else DARK


def _preferences_path() -> Path:
    base = Path(os.environ.get("APPDATA", Path.home()))
    return base / "ChweziDocumentSuite" / "preferences.json"


def load_theme(default: str = "dark") -> str:
    """Load the shared appearance preference without failing application startup."""

    override = os.environ.get("CHWEZI_THEME", "").casefold()
    if override in {"light", "dark"}:
        return override
    try:
        value = json.loads(_preferences_path().read_text(encoding="utf-8")).get("theme")
        if value in {"light", "dark"}:
            return value
    except (OSError, ValueError, TypeError):
        pass
    return default


def save_theme(mode: str) -> None:
    """Persist the shared appearance preference under the user's profile."""

    if mode not in {"light", "dark"}:
        raise ValueError("mode must be 'light' or 'dark'")
    try:
        path = _preferences_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"theme": mode}, indent=2) + "\n", encoding="utf-8")
    except OSError:
        # A read-only profile must not prevent the tools from opening.
        pass


def apply_ttk_theme(root, mode: str) -> Palette:
    """Apply the shared semantic theme to a Tk/ttk application."""

    palette = palette_for(mode)
    root.configure(background=palette.surface_base)
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure(
        ".",
        background=palette.surface_base,
        foreground=palette.text_primary,
        fieldbackground=palette.surface_raised,
        bordercolor=palette.border,
        lightcolor=palette.border,
        darkcolor=palette.border,
        troughcolor=palette.surface_sunken,
        font=(BODY_FONT, 10),
    )
    style.configure("App.TFrame", background=palette.surface_base)
    style.configure("Card.TFrame", background=palette.surface_raised)
    style.configure(
        "Title.TLabel",
        background=palette.surface_base,
        foreground=palette.text_primary,
        font=(DISPLAY_FONT, 23, "bold"),
    )
    style.configure(
        "Subtitle.TLabel",
        background=palette.surface_base,
        foreground=palette.text_muted,
        font=(BODY_FONT, 10),
    )
    style.configure(
        "Section.TLabel",
        background=palette.surface_raised,
        foreground=palette.text_primary,
        font=(DISPLAY_FONT, 12, "bold"),
    )
    style.configure(
        "Card.TLabel",
        background=palette.surface_raised,
        foreground=palette.text_primary,
    )
    style.configure(
        "Muted.TLabel",
        background=palette.surface_raised,
        foreground=palette.text_muted,
    )
    style.configure(
        "Status.TLabel",
        background=palette.accent_soft,
        foreground=palette.text_primary,
        padding=(10, 6),
        font=(BODY_FONT, 9, "bold"),
    )
    style.configure(
        "Card.TLabelframe",
        background=palette.surface_raised,
        bordercolor=palette.border,
        relief="solid",
        borderwidth=1,
        padding=14,
    )
    style.configure(
        "Card.TLabelframe.Label",
        background=palette.surface_raised,
        foreground=palette.text_primary,
        font=(DISPLAY_FONT, 11, "bold"),
    )
    style.configure(
        "TEntry",
        fieldbackground=palette.surface_sunken,
        foreground=palette.text_primary,
        insertcolor=palette.text_primary,
        bordercolor=palette.border,
        padding=(10, 8),
    )
    style.map(
        "TEntry",
        bordercolor=[("focus", palette.focus)],
        lightcolor=[("focus", palette.focus)],
        darkcolor=[("focus", palette.focus)],
    )
    style.configure(
        "TCombobox",
        fieldbackground=palette.surface_sunken,
        background=palette.surface_raised,
        foreground=palette.text_primary,
        arrowcolor=palette.text_primary,
        bordercolor=palette.border,
        padding=(8, 6),
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", palette.surface_sunken)],
        foreground=[("readonly", palette.text_primary)],
        bordercolor=[("focus", palette.focus)],
    )
    style.configure(
        "TButton",
        background=palette.surface_sunken,
        foreground=palette.text_primary,
        bordercolor=palette.border,
        padding=(14, 9),
        font=(BODY_FONT, 9, "bold"),
    )
    style.map(
        "TButton",
        background=[("active", palette.surface_hover), ("pressed", palette.accent_soft)],
        bordercolor=[("focus", palette.focus)],
        foreground=[("disabled", palette.text_muted)],
    )
    style.configure(
        "Primary.TButton",
        background=palette.accent,
        foreground=palette.accent_text,
        bordercolor=palette.accent,
        padding=(18, 10),
    )
    style.map(
        "Primary.TButton",
        background=[("active", palette.accent_hover), ("pressed", palette.accent_hover)],
        foreground=[("active", palette.accent_text), ("disabled", palette.text_muted)],
        bordercolor=[("focus", palette.focus)],
    )
    style.configure(
        "TCheckbutton",
        background=palette.surface_raised,
        foreground=palette.text_primary,
        indicatorbackground=palette.surface_sunken,
        indicatorforeground=palette.accent,
        padding=4,
    )
    style.map("TCheckbutton", background=[("active", palette.surface_raised)])
    style.configure(
        "Card.TCheckbutton",
        background=palette.surface_raised,
        foreground=palette.text_primary,
        indicatorbackground=palette.surface_sunken,
        indicatorforeground=palette.accent,
        padding=4,
    )
    style.map("Card.TCheckbutton", background=[("active", palette.surface_raised)])
    style.configure(
        "TRadiobutton",
        background=palette.surface_raised,
        foreground=palette.text_primary,
        indicatorbackground=palette.surface_sunken,
        indicatorforeground=palette.accent,
        padding=4,
    )
    style.map("TRadiobutton", background=[("active", palette.surface_raised)])
    style.configure(
        "Card.TRadiobutton",
        background=palette.surface_raised,
        foreground=palette.text_primary,
        indicatorbackground=palette.surface_sunken,
        indicatorforeground=palette.accent,
        padding=4,
    )
    style.map("Card.TRadiobutton", background=[("active", palette.surface_raised)])
    style.configure(
        "Horizontal.TProgressbar",
        background=palette.accent,
        troughcolor=palette.surface_sunken,
        bordercolor=palette.surface_sunken,
        lightcolor=palette.accent,
        darkcolor=palette.accent,
        thickness=10,
    )
    style.configure(
        "Horizontal.TScale",
        background=palette.surface_raised,
        troughcolor=palette.surface_sunken,
    )
    root.option_add("*TCombobox*Listbox.background", palette.surface_raised)
    root.option_add("*TCombobox*Listbox.foreground", palette.text_primary)
    root.option_add("*TCombobox*Listbox.selectBackground", palette.accent)
    root.option_add("*TCombobox*Listbox.selectForeground", palette.accent_text)
    return palette


def style_text_widget(widget, palette: Palette) -> None:
    widget.configure(
        background=palette.surface_sunken,
        foreground=palette.text_primary,
        insertbackground=palette.text_primary,
        selectbackground=palette.accent,
        selectforeground=palette.accent_text,
        relief="flat",
        borderwidth=0,
        highlightthickness=1,
        highlightbackground=palette.border,
        highlightcolor=palette.focus,
    )
