"""Finite document and conversion policy values."""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path


class DocumentFormat(StrEnum):
    PDF = "pdf"
    PDF_A = "pdfa"
    DOC = "doc"
    DOCX = "docx"
    PPTX = "pptx"
    XLSX = "xlsx"
    EPUB = "epub"
    HTML = "html"
    MARKDOWN = "markdown"
    TEXT = "text"
    RTF = "rtf"
    ODT = "odt"
    ODP = "odp"
    ODS = "ods"
    CSV = "csv"
    JPEG = "jpeg"
    PNG = "png"
    TIFF = "tiff"
    BMP = "bmp"
    WEBP = "webp"

    @classmethod
    def from_path(cls, path: Path) -> DocumentFormat:
        extension = path.suffix.lower().lstrip(".")
        aliases = {"md": cls.MARKDOWN, "jpg": cls.JPEG, "tif": cls.TIFF}
        if extension in aliases:
            return aliases[extension]
        try:
            return cls(extension)
        except ValueError as exc:
            from .errors import UnsupportedFormatError

            raise UnsupportedFormatError(
                detail=f"No registered format matches extension {path.suffix!r}.",
                suggested_action="Choose a supported input file or inspect `chwezi capabilities`.",
            ) from exc

    @classmethod
    def parse(cls, value: str) -> DocumentFormat:
        normalised = value.strip().lower().replace("-", "").replace("_", "")
        aliases = {"md": cls.MARKDOWN, "pdfa": cls.PDF_A, "jpg": cls.JPEG, "tif": cls.TIFF}
        if normalised in aliases:
            return aliases[normalised]
        return cls(normalised)

    @property
    def extension(self) -> str:
        return {
            self.MARKDOWN: ".md",
            self.PDF_A: ".pdf",
            self.JPEG: ".jpg",
            self.TIFF: ".tiff",
        }.get(self, f".{self.value}")


class OverwritePolicy(StrEnum):
    FAIL = "fail"
    SKIP = "skip"
    RENAME = "rename"
    OVERWRITE = "overwrite"


class FidelityClass(StrEnum):
    EXACT = "exact"
    HIGH = "high"
    STRUCTURED = "structured"
    TEXT_ONLY = "text-only"
    EXPERIMENTAL = "experimental"
