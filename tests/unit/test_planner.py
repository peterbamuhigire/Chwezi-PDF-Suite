import pytest

from chwezi_docs.application.capability_service import CapabilityReport
from chwezi_docs.conversion.planner import ConversionPlanner
from chwezi_docs.conversion.registry import ConverterSpec
from chwezi_docs.domain.errors import MissingCapabilityError, UnsupportedConversionError
from chwezi_docs.domain.formats import DocumentFormat, FidelityClass


class AvailableCapabilities:
    def inspect(self, converter: ConverterSpec) -> CapabilityReport:
        return CapabilityReport(converter=converter, available=True, missing=())


class MissingCapabilities:
    def inspect(self, converter: ConverterSpec) -> CapabilityReport:
        return CapabilityReport(converter=converter, available=False, missing=("tool missing",))


def test_planner_prefers_non_lossy_lower_cost_route() -> None:
    expensive = ConverterSpec(
        name="expensive",
        source_format=DocumentFormat.DOCX,
        target_format=DocumentFormat.MARKDOWN,
        fidelity=FidelityClass.TEXT_ONLY,
        lossy=True,
        cost=1,
    )
    preferred = ConverterSpec(
        name="preferred",
        source_format=DocumentFormat.DOCX,
        target_format=DocumentFormat.MARKDOWN,
        fidelity=FidelityClass.STRUCTURED,
        lossy=False,
        cost=2,
    )
    planner = ConversionPlanner(
        registry=(expensive, preferred),
        capabilities=AvailableCapabilities(),  # type: ignore[arg-type]
    )

    plan = planner.plan(DocumentFormat.DOCX, DocumentFormat.MARKDOWN)

    assert plan.backends == ("preferred",)


def test_planner_terminates_when_graph_contains_cycle() -> None:
    registry = (
        ConverterSpec(
            name="docx-html",
            source_format=DocumentFormat.DOCX,
            target_format=DocumentFormat.HTML,
            fidelity=FidelityClass.STRUCTURED,
        ),
        ConverterSpec(
            name="html-docx",
            source_format=DocumentFormat.HTML,
            target_format=DocumentFormat.DOCX,
            fidelity=FidelityClass.STRUCTURED,
        ),
        ConverterSpec(
            name="html-markdown",
            source_format=DocumentFormat.HTML,
            target_format=DocumentFormat.MARKDOWN,
            fidelity=FidelityClass.STRUCTURED,
        ),
    )
    planner = ConversionPlanner(
        registry=registry,
        capabilities=AvailableCapabilities(),  # type: ignore[arg-type]
    )

    plan = planner.plan(DocumentFormat.DOCX, DocumentFormat.MARKDOWN)

    assert plan.backends == ("docx-html", "html-markdown")


def test_planner_distinguishes_missing_capability_from_unsupported_route() -> None:
    converter = ConverterSpec(
        name="docx-markdown",
        source_format=DocumentFormat.DOCX,
        target_format=DocumentFormat.MARKDOWN,
        fidelity=FidelityClass.STRUCTURED,
    )
    unavailable = ConversionPlanner(
        registry=(converter,),
        capabilities=MissingCapabilities(),  # type: ignore[arg-type]
    )

    with pytest.raises(MissingCapabilityError):
        unavailable.plan(DocumentFormat.DOCX, DocumentFormat.MARKDOWN)

    with pytest.raises(UnsupportedConversionError):
        ConversionPlanner(registry=()).plan(DocumentFormat.PDF, DocumentFormat.XLSX)
