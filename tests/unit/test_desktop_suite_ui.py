from __future__ import annotations

import importlib.util
import re
import sys
import tomllib
from pathlib import Path

import pytest

from ui_icons import ICON_ROOT, icon_source
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


def test_icon_catalog_paint_references_are_resolved() -> None:
    svg_paths = sorted(ICON_ROOT.glob("*/*.svg"))

    assert len(svg_paths) == 89
    for path in svg_paths:
        content = path.read_text(encoding="utf-8")
        references = set(re.findall(r"url\(#([^)]+)\)", content))
        identifiers = set(re.findall(r"\bid\s*=\s*['\"]([^'\"]+)['\"]", content))
        assert references <= identifiers, path
        assert "<script" not in content.casefold()


def test_every_svg_has_light_and_dark_desktop_rasters() -> None:
    for svg_path in ICON_ROOT.glob("*/*.svg"):
        group = svg_path.parent.name
        for theme in ("light", "dark"):
            raster = ICON_ROOT / "raster" / theme / group / f"{svg_path.stem}.png"
            assert raster.is_file(), raster
            assert raster.stat().st_size > 100, raster


def test_web_stylesheet_icon_urls_resolve() -> None:
    stylesheet_path = PROJECT_ROOT / "static" / "css" / "style.css"
    stylesheet = stylesheet_path.read_text(encoding="utf-8")
    icon_urls = re.findall(r'url\("(\.\./icons/[^"?]+)"\)', stylesheet)

    assert icon_urls
    for icon_url in icon_urls:
        icon_path = (stylesheet_path.parent / icon_url).resolve()
        assert icon_path.is_relative_to(ICON_ROOT.resolve())
        assert icon_path.is_file(), icon_path


def test_manifest_and_pyinstaller_spec_use_distinct_app_icons() -> None:
    manifest_path = PROJECT_ROOT / "packaging" / "desktop-suite.toml"
    manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    expected = {
        manifest["product"]["launcher_executable"]: manifest["product"]["icon"],
        **{app["executable"]: app["icon"] for app in manifest["applications"]},
    }
    spec_text = (PROJECT_ROOT / "packaging" / "generated" / "chwezi-document-suite.spec").read_text(
        encoding="utf-8"
    )

    for executable, relative_icon in expected.items():
        assert (PROJECT_ROOT / relative_icon).is_file()
        escaped_executable = re.escape(executable)
        escaped_icon = re.escape(relative_icon)
        block_pattern = (
            rf"name='{escaped_executable}'.+?icon=str\(PROJECT_ROOT / '{escaped_icon}'\)"
        )
        assert re.search(block_pattern, spec_text, flags=re.DOTALL), executable


def test_icon_source_rejects_path_traversal() -> None:
    with pytest.raises(ValueError):
        icon_source("navigation", "../settings")
