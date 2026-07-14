"""Non-destructive output naming and validation primitives."""

from __future__ import annotations

from pathlib import Path

from chwezi_docs.domain.errors import InvalidDocumentError, OutputCollisionError
from chwezi_docs.domain.formats import OverwritePolicy


def select_output_path(path: Path, policy: OverwritePolicy) -> tuple[Path, bool]:
    """Return a collision-safe path and whether an existing output should be skipped."""
    if not path.exists():
        return path, False
    if policy is OverwritePolicy.OVERWRITE:
        return path, False
    if policy is OverwritePolicy.SKIP:
        return path, True
    if policy is OverwritePolicy.FAIL:
        raise OutputCollisionError(
            detail=f"Output exists: {path}",
            suggested_action="Choose rename, skip, overwrite, or a different output directory.",
        )

    counter = 1
    while True:
        candidate = path.with_name(f"{path.stem}_{counter}{path.suffix}")
        if not candidate.exists():
            return candidate, False
        counter += 1


def validate_text_output(path: Path) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise InvalidDocumentError(
            detail=f"Converter output is missing or empty: {path}",
            suggested_action=(
                "Review converter warnings and verify the input contains extractable text."
            ),
        )
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeError as exc:
        raise InvalidDocumentError(
            detail=f"Output is not valid UTF-8: {path}",
            suggested_action="Report the backend and input format in a diagnostic bundle.",
        ) from exc
    if not text.strip():
        raise InvalidDocumentError(
            detail=f"Output contains no non-whitespace text: {path}",
            suggested_action="Enable OCR for scanned input when that capability is available.",
        )
