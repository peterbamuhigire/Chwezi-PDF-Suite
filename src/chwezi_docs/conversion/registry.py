"""Declarative registry for implemented and planned conversion edges."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from chwezi_docs.domain.formats import DocumentFormat, FidelityClass


class RequirementKind(StrEnum):
    PYTHON_MODULE = "python-module"
    EXECUTABLE = "executable"
    ANY = "any"


@dataclass(frozen=True, slots=True)
class Requirement:
    name: str
    kind: RequirementKind
    values: tuple[str, ...]
    install_hint: str


@dataclass(frozen=True, slots=True)
class ConverterSpec:
    name: str
    source_format: DocumentFormat
    target_format: DocumentFormat
    fidelity: FidelityClass
    requirements: tuple[Requirement, ...] = ()
    lossy: bool = False
    cost: int = 1
    implemented: bool = True
    description: str = ""


def default_registry() -> tuple[ConverterSpec, ...]:
    pdf_requirements = (
        Requirement(
            name="PDF extraction packages",
            kind=RequirementKind.PYTHON_MODULE,
            values=("pdfplumber", "pypdf"),
            install_hint='pip install "chwezi-document-suite[extract]"',
        ),
    )
    pptx_requirements = (
        Requirement(
            name="PowerPoint extraction package",
            kind=RequirementKind.PYTHON_MODULE,
            values=("pptx",),
            install_hint='pip install "chwezi-document-suite[extract]"',
        ),
    )
    office_requirement = Requirement(
        name="Legacy Word conversion backend",
        kind=RequirementKind.ANY,
        values=("soffice", "libreoffice", "win32com.client"),
        install_hint="Install LibreOffice, or Microsoft Word plus the `office` extra on Windows.",
    )

    return (
        ConverterSpec(
            name="legacy-pdf-markdown",
            source_format=DocumentFormat.PDF,
            target_format=DocumentFormat.MARKDOWN,
            fidelity=FidelityClass.TEXT_ONLY,
            requirements=pdf_requirements,
            lossy=True,
            description="Heuristic PDF text and heading extraction; no OCR or images.",
        ),
        ConverterSpec(
            name="legacy-docx-markdown",
            source_format=DocumentFormat.DOCX,
            target_format=DocumentFormat.MARKDOWN,
            fidelity=FidelityClass.STRUCTURED,
            requirements=pdf_requirements,
            lossy=True,
            description="OOXML paragraphs, headings, lists and basic table rows.",
        ),
        ConverterSpec(
            name="legacy-epub-markdown",
            source_format=DocumentFormat.EPUB,
            target_format=DocumentFormat.MARKDOWN,
            fidelity=FidelityClass.STRUCTURED,
            requirements=pdf_requirements,
            lossy=True,
            description="EPUB spine HTML to basic Markdown blocks.",
        ),
        ConverterSpec(
            name="legacy-doc-markdown",
            source_format=DocumentFormat.DOC,
            target_format=DocumentFormat.MARKDOWN,
            fidelity=FidelityClass.TEXT_ONLY,
            requirements=(*pdf_requirements, office_requirement),
            lossy=True,
            cost=3,
            description="Legacy Word conversion through LibreOffice or Word before extraction.",
        ),
        ConverterSpec(
            name="legacy-pptx-markdown",
            source_format=DocumentFormat.PPTX,
            target_format=DocumentFormat.MARKDOWN,
            fidelity=FidelityClass.STRUCTURED,
            requirements=pptx_requirements,
            lossy=True,
            description="Slide-preserving text, list and table extraction; no images or notes.",
        ),
    )
