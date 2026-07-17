#!/usr/bin/env python3
"""Validate Chwezi SVGs and build raster assets for the desktop interfaces."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ICON_ROOT = PROJECT_ROOT / "static" / "icons"
SOURCE_GROUPS = ("actions", "apps", "file-types", "navigation", "status")
APP_ICON_SIZES = (16, 20, 24, 32, 40, 48, 64, 128, 256)
PAINT_REFERENCE_RE = re.compile(r"url\(#([^)]+)\)")
ID_RE = re.compile(r"\bid\s*=\s*['\"]([^'\"]+)['\"]")


def find_chrome() -> Path:
    """Return an installed Chromium browser suitable for deterministic SVG rendering."""

    candidates = (
        Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
        Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
        Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    resolved = shutil.which("chrome") or shutil.which("msedge")
    if resolved:
        return Path(resolved)
    raise FileNotFoundError("Chrome or Microsoft Edge is required to rebuild icon PNGs")


def source_svgs(groups: tuple[str, ...] = SOURCE_GROUPS) -> list[tuple[str, Path]]:
    """Return the declared icon groups and their SVG files in stable order."""

    files: list[tuple[str, Path]] = []
    for group in groups:
        group_dir = ICON_ROOT / group
        if not group_dir.is_dir():
            raise FileNotFoundError(f"Missing icon group: {group_dir}")
        files.extend((group, path) for path in sorted(group_dir.glob("*.svg")))
    return files


def validate_svg(path: Path) -> None:
    """Reject SVG paint references that have no matching element id."""

    content = path.read_text(encoding="utf-8")
    references = set(PAINT_REFERENCE_RE.findall(content))
    ids = set(ID_RE.findall(content))
    missing = sorted(references - ids)
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"{path.relative_to(PROJECT_ROOT)} has missing paint ids: {joined}")
    if "<script" in content.casefold():
        raise ValueError(f"{path.relative_to(PROJECT_ROOT)} contains a script element")


def render_svg(
    browser: Path,
    source: Path,
    destination: Path,
    *,
    size: int,
    dark: bool,
    profile_dir: Path,
) -> None:
    """Render one transparent square PNG through Chromium."""

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.unlink(missing_ok=True)
    svg_content = source.read_text(encoding="utf-8")
    svg_start = svg_content.find("<svg")
    svg_end = svg_content.rfind("</svg>")
    if svg_start < 0 or svg_end < 0:
        raise ValueError(f"Could not find the SVG root in {source}")
    inline_svg = svg_content[svg_start : svg_end + len("</svg>")]
    cg1_values = re.findall(r"--cg1\s*:\s*(#[0-9a-fA-F]{6})", inline_svg)
    cg2_values = re.findall(r"--cg2\s*:\s*(#[0-9a-fA-F]{6})", inline_svg)
    default_colours = ("#69C8BD", "#89D8CE") if dark else ("#006C67", "#2F7F78")
    colour_index = -1 if dark else 0
    colours = (
        cg1_values[colour_index] if cg1_values else default_colours[0],
        cg2_values[colour_index] if cg2_values else default_colours[1],
    )
    inline_svg = inline_svg.replace("var(--cg1)", colours[0]).replace("var(--cg2)", colours[1])
    root_match = re.search(r"<svg\b([^>]*)>", inline_svg, flags=re.DOTALL)
    if root_match is None:
        raise ValueError(f"Could not parse the SVG root in {source}")
    attributes = re.sub(
        r"\s(?:width|height|preserveAspectRatio)\s*=\s*(['\"]).*?\1",
        "",
        root_match.group(1),
        flags=re.DOTALL,
    )
    sized_root = (
        f'<svg{attributes} width="{size}" height="{size}" preserveAspectRatio="xMidYMid meet">'
    )
    themed_svg = inline_svg[: root_match.start()] + sized_root + inline_svg[root_match.end() :]
    render_source = profile_dir.parent / f"{profile_dir.name}.svg"
    render_source.write_text(themed_svg, encoding="utf-8")
    command = [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--no-first-run",
        "--disable-default-apps",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=1000",
        "--default-background-color=00000000",
        "--force-device-scale-factor=1",
        f"--window-size={size},{size}",
        f"--user-data-dir={profile_dir}",
        f"--screenshot={destination}",
    ]
    if dark:
        command.append("--force-dark-mode")
    command.append(render_source.as_uri())
    completed = subprocess.run(  # noqa: S603 - fixed local browser executable and arguments.
        command, capture_output=True, text=True, check=False
    )
    if completed.returncode != 0 or not destination.is_file():
        detail = (completed.stderr or completed.stdout).strip()
        raise RuntimeError(f"Could not render {source.name}: {detail}")
    with Image.open(destination) as rendered:
        if rendered.convert("RGBA").getbbox() is None:
            raise RuntimeError(f"Rendered icon is fully transparent: {source.name}")


def build_assets(groups: tuple[str, ...] = SOURCE_GROUPS) -> tuple[int, int]:
    """Build light/dark PNGs and multi-size Windows icons."""

    browser = find_chrome()
    svg_files = source_svgs(groups)
    for _group, path in svg_files:
        validate_svg(path)

    raster_root = ICON_ROOT / "raster"
    if groups == SOURCE_GROUPS and raster_root.exists():
        shutil.rmtree(raster_root)

    with tempfile.TemporaryDirectory(prefix="chwezi-icons-") as temporary:
        temporary_root = Path(temporary)
        jobs: list[tuple[int, str, Path, Path, int]] = []
        job_number = 0
        for group, source in svg_files:
            size = 512 if group == "apps" else 128
            for mode in ("light", "dark"):
                destination = raster_root / mode / group / f"{source.stem}.png"
                jobs.append((job_number, mode, source, destination, size))
                job_number += 1

        def run_render(job: tuple[int, str, Path, Path, int]) -> None:
            number, mode, source, destination, size = job
            profile_dir = temporary_root / f"browser-profile-{number}"
            render_svg(
                browser,
                source,
                destination,
                size=size,
                dark=mode == "dark",
                profile_dir=profile_dir,
            )

        with ThreadPoolExecutor(max_workers=8) as executor:
            for _ in executor.map(run_render, jobs):
                pass

    if "apps" in groups:
        app_dir = ICON_ROOT / "apps"
        for app_svg in sorted(app_dir.glob("app-*.svg")):
            light_png = raster_root / "light" / "apps" / f"{app_svg.stem}.png"
            with Image.open(light_png) as image:
                image.save(
                    app_dir / f"{app_svg.stem}.ico",
                    format="ICO",
                    sizes=[(size, size) for size in APP_ICON_SIZES],
                )

    return len(svg_files), len(svg_files) * 2


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate SVG references without rebuilding PNG and ICO files.",
    )
    parser.add_argument(
        "--group",
        action="append",
        choices=SOURCE_GROUPS,
        help="Rebuild one or more icon groups without deleting other raster output.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    groups = tuple(dict.fromkeys(args.group)) if args.group else SOURCE_GROUPS
    files = source_svgs(groups)
    if args.validate_only:
        for _group, path in files:
            validate_svg(path)
        print(f"Validated {len(files)} SVG files")
        return 0

    svg_count, png_count = build_assets(groups)
    print(f"Built {png_count} PNGs and {len(list((ICON_ROOT / 'apps').glob('*.ico')))} ICOs")
    print(f"Validated {svg_count} SVG sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
