#!/usr/bin/env python3
"""
Runtime dependency bootstrap helpers for standalone tools.

These converters are often run directly from a checkout. Installing missing
Python packages at startup keeps that workflow usable without a separate setup
step.
"""

from __future__ import annotations

import importlib
import os
import subprocess
import sys


def ensure_packages(requirements: list[tuple[str, str]]) -> None:
    missing = [(module_name, package_name) for module_name, package_name in requirements if not _can_import(module_name)]
    if not missing:
        return

    if os.environ.get("PYPDFLIBRARIAN_NO_AUTO_INSTALL"):
        packages = ", ".join(package_name for _, package_name in missing)
        raise RuntimeError(
            f"Missing required package(s): {packages}. Install them or unset PYPDFLIBRARIAN_NO_AUTO_INSTALL."
        )

    packages = [package_name for _, package_name in missing]
    print(f"Installing missing Python package(s): {', '.join(packages)}")
    command = [sys.executable, "-m", "pip", "install", *packages]
    try:
        subprocess.check_call(command)
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"Could not auto-install required package(s): {', '.join(packages)}") from exc

    still_missing = [module_name for module_name, _ in missing if not _can_import(module_name)]
    if still_missing:
        raise RuntimeError(f"Installed packages, but imports still failed: {', '.join(still_missing)}")


def _can_import(module_name: str) -> bool:
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False
