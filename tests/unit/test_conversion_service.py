from pathlib import Path

import pytest

from chwezi_docs.application.capability_service import CapabilityReport
from chwezi_docs.application.conversion_service import ConversionService
from chwezi_docs.conversion.planner import ConversionPlanner
from chwezi_docs.conversion.registry import ConverterSpec
from chwezi_docs.domain.errors import ConversionFailedError
from chwezi_docs.domain.formats import DocumentFormat, FidelityClass, OverwritePolicy
from chwezi_docs.domain.results import ConversionRequest


class AvailableCapabilities:
    def inspect(self, converter: ConverterSpec) -> CapabilityReport:
        return CapabilityReport(converter=converter, available=True, missing=())


def make_service() -> ConversionService:
    converter = ConverterSpec(
        name="test-docx-markdown",
        source_format=DocumentFormat.DOCX,
        target_format=DocumentFormat.MARKDOWN,
        fidelity=FidelityClass.STRUCTURED,
    )
    planner = ConversionPlanner(
        registry=(converter,),
        capabilities=AvailableCapabilities(),  # type: ignore[arg-type]
    )
    return ConversionService(planner)


def test_conversion_stages_validates_and_promotes_atomically(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "input.docx"
    source.write_bytes(b"fixture")
    output_dir = tmp_path / "output"

    def fake_backend(source_path: Path, staging: Path) -> list[Path]:
        output = staging / f"{source_path.stem}.md"
        output.write_text("# Converted\n", encoding="utf-8")
        return [output]

    monkeypatch.setattr(
        ConversionService,
        "_run_transitional_backend",
        staticmethod(fake_backend),
    )
    result = make_service().convert(ConversionRequest(source, DocumentFormat.MARKDOWN, output_dir))

    assert result.output_files == (output_dir / "input.md",)
    assert result.output_files[0].read_text(encoding="utf-8") == "# Converted\n"
    assert not list(output_dir.glob(".chwezi-*"))


def test_failed_conversion_leaves_no_final_placeholder(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source = tmp_path / "input.docx"
    source.write_bytes(b"fixture")
    output_dir = tmp_path / "output"

    monkeypatch.setattr(ConversionService, "_run_transitional_backend", lambda *_: [])

    with pytest.raises(ConversionFailedError):
        make_service().convert(
            ConversionRequest(
                source,
                DocumentFormat.MARKDOWN,
                output_dir,
                OverwritePolicy.RENAME,
            )
        )

    assert not (output_dir / "input.md").exists()
    assert not list(output_dir.glob(".chwezi-*"))
