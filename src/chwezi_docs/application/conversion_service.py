"""Shared conversion orchestration with staging, validation, and honest warnings."""

from __future__ import annotations

import importlib
import os
import tempfile
from pathlib import Path
from time import perf_counter
from typing import Any

from chwezi_docs.conversion.planner import ConversionPlanner
from chwezi_docs.domain.errors import ConversionFailedError, InvalidDocumentError
from chwezi_docs.domain.formats import DocumentFormat
from chwezi_docs.domain.jobs import JobStatus
from chwezi_docs.domain.results import ConversionRequest, ConversionResult, ConversionWarning
from chwezi_docs.infrastructure.filesystem import select_output_path, validate_text_output


class ConversionService:
    """Execute currently implemented conversions through one application boundary."""

    def __init__(self, planner: ConversionPlanner | None = None) -> None:
        self.planner = planner or ConversionPlanner()

    def convert(self, request: ConversionRequest) -> ConversionResult:
        started = perf_counter()
        source = request.source.resolve()
        if not source.is_file():
            raise InvalidDocumentError(
                detail=f"Input file does not exist or is not a regular file: {source}",
                suggested_action=(
                    "Provide one existing file. Batch directory support is not in this alpha."
                ),
            )

        source_format = DocumentFormat.from_path(source)
        plan = self.planner.plan(source_format, request.target_format)
        if len(plan.steps) != 1 or request.target_format is not DocumentFormat.MARKDOWN:
            raise ConversionFailedError(
                detail="The alpha executor supports one-step Markdown routes only.",
                suggested_action="Use a route reported as available by `chwezi capabilities`.",
            )

        output_dir = request.output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        desired = output_dir / f"{source.stem}{request.target_format.extension}"
        final_path, skipped = select_output_path(desired, request.overwrite_policy)
        if skipped:
            warning = ConversionWarning(
                code="OUTPUT_SKIPPED",
                message=f"Existing output was preserved: {final_path}",
            )
            return ConversionResult(
                status=JobStatus.COMPLETED_WITH_WARNINGS,
                source=source,
                output_files=(final_path,),
                warnings=(warning,),
                backends=plan.backends,
                duration_seconds=perf_counter() - started,
                metadata={"skipped": True},
            )

        with tempfile.TemporaryDirectory(prefix=".chwezi-", dir=output_dir) as temp_name:
            staged_dir = Path(temp_name)
            staged_outputs = self._run_transitional_backend(source, staged_dir)
            expected = staged_dir / f"{source.stem}.md"
            staged_path = (
                expected if expected in staged_outputs else self._single_output(staged_outputs)
            )
            validate_text_output(staged_path)
            os.replace(staged_path, final_path)

        warning = ConversionWarning(
            code="LOSSY_TEXT_EXTRACTION",
            message=(
                "This route extracts document structure and text; visual layout, images, notes, "
                "or unsupported elements may be omitted."
            ),
        )
        return ConversionResult(
            status=JobStatus.COMPLETED_WITH_WARNINGS,
            source=source,
            output_files=(final_path,),
            warnings=(warning,),
            backends=plan.backends,
            duration_seconds=perf_counter() - started,
            metadata={
                "source_format": source_format.value,
                "target_format": request.target_format.value,
                "validation": "utf8-nonempty",
                "adapter": "transitional-legacy",
            },
        )

    @staticmethod
    def _single_output(outputs: list[Path]) -> Path:
        if len(outputs) != 1:
            raise ConversionFailedError(
                detail=f"Expected one output but the backend returned {len(outputs)}.",
                suggested_action="Export diagnostics and report the backend result count.",
            )
        return outputs[0]

    @staticmethod
    def _run_transitional_backend(source: Path, output_dir: Path) -> list[Path]:
        try:
            if source.suffix.lower() == ".pptx":
                module: Any = importlib.import_module("pptx_to_epub")
                converter = module.PowerPointToMarkdownConverter()
            else:
                module = importlib.import_module("pdf_to_epub")
                converter = module.PdfToMarkdownConverter()
            return [Path(path) for path in converter.convert(source, output_dir)]
        except Exception as exc:
            raise ConversionFailedError(
                detail=f"Transitional backend failed: {type(exc).__name__}: {exc}",
                suggested_action="Check the input, optional dependencies, and capability report.",
                retryable=False,
            ) from exc
