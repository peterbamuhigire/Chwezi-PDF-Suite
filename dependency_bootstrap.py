#!/usr/bin/env python3
"""Compatibility dependency checks for legacy standalone tools.

The historical helper installed packages during application startup. It now
reports the exact installation command and leaves environment changes to the
user or package manager.
"""

from __future__ import annotations

import importlib


def ensure_packages(requirements: list[tuple[str, str]]) -> None:
    missing = [
        (module_name, package_name)
        for module_name, package_name in requirements
        if not _can_import(module_name)
    ]
    if not missing:
        return

    packages = " ".join(package_name for _, package_name in missing)
    raise RuntimeError(
        "Missing optional dependency or dependencies: "
        f"{packages}. Install them explicitly with: python -m pip install {packages}"
    )


def _can_import(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False
