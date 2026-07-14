"""Typed conversion requests, warnings, and results."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .formats import DocumentFormat, OverwritePolicy
from .jobs import JobStatus


@dataclass(frozen=True, slots=True)
class ConversionWarning:
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {"code": self.code, "message": self.message}


@dataclass(frozen=True, slots=True)
class ConversionRequest:
    source: Path
    target_format: DocumentFormat
    output_dir: Path
    overwrite_policy: OverwritePolicy = OverwritePolicy.RENAME
    options: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "source", Path(self.source).expanduser())
        object.__setattr__(self, "output_dir", Path(self.output_dir).expanduser())


@dataclass(frozen=True, slots=True)
class ConversionResult:
    status: JobStatus
    source: Path
    output_files: tuple[Path, ...]
    warnings: tuple[ConversionWarning, ...]
    backends: tuple[str, ...]
    duration_seconds: float
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status.value,
            "source": str(self.source),
            "output_files": [str(path) for path in self.output_files],
            "warnings": [warning.to_dict() for warning in self.warnings],
            "backends": list(self.backends),
            "duration_seconds": round(self.duration_seconds, 6),
            "metadata": dict(self.metadata),
        }
