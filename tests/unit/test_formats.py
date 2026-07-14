from pathlib import Path

import pytest

from chwezi_docs.domain.errors import UnsupportedFormatError
from chwezi_docs.domain.formats import DocumentFormat


@pytest.mark.parametrize(
    ("filename", "expected"),
    [
        ("report.pdf", DocumentFormat.PDF),
        ("notes.md", DocumentFormat.MARKDOWN),
        ("scan.TIF", DocumentFormat.TIFF),
        ("photo.jpg", DocumentFormat.JPEG),
    ],
)
def test_format_detection_uses_explicit_aliases(filename: str, expected: DocumentFormat) -> None:
    assert DocumentFormat.from_path(Path(filename)) is expected


def test_unknown_extension_has_actionable_error() -> None:
    with pytest.raises(UnsupportedFormatError) as captured:
        DocumentFormat.from_path(Path("archive.unknown"))

    assert captured.value.code == "UNSUPPORTED_FORMAT"
    assert "capabilities" in captured.value.suggested_action
