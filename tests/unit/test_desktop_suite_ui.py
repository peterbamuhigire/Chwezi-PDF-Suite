from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from ui_theme import DARK, LIGHT, colour

PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_launcher():
    spec = importlib.util.spec_from_file_location(
        "chwezi_suite_launcher",
        PROJECT_ROOT / "index-app.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _relative_luminance(hex_colour: str) -> float:
    channels = [int(hex_colour[index : index + 2], 16) / 255 for index in (1, 3, 5)]

    def linear(channel: float) -> float:
        return channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4

    red, green, blue = (linear(channel) for channel in channels)
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def _contrast(foreground: str, background: str) -> float:
    light, dark = sorted(
        (_relative_luminance(foreground), _relative_luminance(background)),
        reverse=True,
    )
    return (light + 0.05) / (dark + 0.05)


@pytest.mark.parametrize("palette", [LIGHT, DARK])
def test_theme_text_pairs_meet_wcag_body_contrast(palette) -> None:
    assert _contrast(palette.text_primary, palette.surface_base) >= 4.5
    assert _contrast(palette.text_muted, palette.surface_base) >= 4.5
    assert _contrast(palette.text_primary, palette.surface_raised) >= 4.5
    assert _contrast(palette.accent_text, palette.accent) >= 4.5


def test_customtkinter_colours_expose_light_and_dark_values() -> None:
    assert colour("surface_base") == (LIGHT.surface_base, DARK.surface_base)
    assert colour("text_primary") == (LIGHT.text_primary, DARK.text_primary)


def test_frozen_launcher_resolves_installed_sibling_executable(monkeypatch) -> None:
    launcher = _load_launcher()
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", r"C:\Program Files\Chwezi\ChweziDocumentSuite.exe")

    command = launcher.command_for(launcher.TOOLS[1])

    assert command == [r"C:\Program Files\Chwezi\ChweziSigner.exe"]


def test_source_launcher_uses_python_entry_script(monkeypatch) -> None:
    launcher = _load_launcher()
    monkeypatch.delattr(sys, "frozen", raising=False)
    monkeypatch.setattr(sys, "executable", r"C:\Python312\python.exe")

    command = launcher.command_for(launcher.TOOLS[2])

    assert command[0] == r"C:\Python312\python.exe"
    assert command[1].endswith("documents_to_markdown.py")
    assert command[2:] == ["--gui"]
