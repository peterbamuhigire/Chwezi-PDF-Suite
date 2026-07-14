from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest


def create_minimal_docx(path: Path) -> None:
    document = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Audit Heading</w:t></w:r></w:p>
    <w:p><w:r><w:t>Preserved paragraph text.</w:t></w:r></w:p>
  </w:body>
</w:document>"""
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr("word/document.xml", document)


@pytest.mark.integration
def test_public_suite_preserves_docx_markdown_shape(tmp_path: Path) -> None:
    pytest.importorskip("pdfplumber")
    from chwezi_docs import DocumentSuite

    source = tmp_path / "sample.docx"
    create_minimal_docx(source)

    result = DocumentSuite().convert(source, "markdown", tmp_path / "output")
    markdown = result.output_files[0].read_text(encoding="utf-8")

    assert markdown == "# Audit Heading\n\nPreserved paragraph text.\n"
    assert result.metadata["adapter"] == "transitional-legacy"
