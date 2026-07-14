"""Public Python facade for Chwezi Document Suite."""

from __future__ import annotations

from pathlib import Path

from .application.conversion_service import ConversionService
from .domain.formats import DocumentFormat, OverwritePolicy
from .domain.results import ConversionRequest, ConversionResult


class DocumentSuite:
    """Stable high-level API for document operations."""

    def __init__(self, conversion_service: ConversionService | None = None) -> None:
        self._conversion_service = conversion_service or ConversionService()

    def convert(
        self,
        source: Path,
        target_format: str | DocumentFormat,
        output_dir: Path,
        overwrite_policy: OverwritePolicy = OverwritePolicy.RENAME,
    ) -> ConversionResult:
        target = (
            target_format
            if isinstance(target_format, DocumentFormat)
            else DocumentFormat.parse(target_format)
        )
        return self._conversion_service.convert(
            ConversionRequest(
                source=source,
                target_format=target,
                output_dir=output_dir,
                overwrite_policy=overwrite_policy,
            )
        )
