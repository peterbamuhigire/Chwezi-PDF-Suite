"""Hostile DOCX/EPUB containers must be rejected before they exhaust memory (R-005)."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("pptx")
pytest.importorskip("pypdf")

import documents_to_markdown as dtm

DOCUMENT = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    "<w:body><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:body></w:document>"
)


def write_docx(path: Path, document_xml: str) -> Path:
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr("word/document.xml", document_xml)
    return path


@pytest.mark.security
def test_highly_compressed_member_is_rejected(tmp_path: Path) -> None:
    bomb = write_docx(tmp_path / "bomb.docx", DOCUMENT.format(text=" " * (8 * 1024 * 1024)))

    with pytest.raises(ValueError, match="suspiciously compressed"):
        dtm.DocumentToMarkdownConverter().extract_docx_blocks(bomb)


@pytest.mark.security
def test_oversized_member_is_rejected(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(dtm, "MAX_ARCHIVE_MEMBER_BYTES", 1024)
    large = write_docx(tmp_path / "large.docx", DOCUMENT.format(text="word " * 1000))

    with pytest.raises(ValueError, match="too large"):
        dtm.DocumentToMarkdownConverter().extract_docx_blocks(large)


@pytest.mark.security
def test_entity_expansion_is_rejected(tmp_path: Path) -> None:
    laughs = (
        '<?xml version="1.0"?><!DOCTYPE w [<!ENTITY a "lol"><!ENTITY b "&a;&a;&a;&a;">]>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body><w:p><w:r><w:t>&b;</w:t></w:r></w:p></w:body></w:document>"
    )
    docx = write_docx(tmp_path / "laughs.docx", laughs)

    with pytest.raises(ValueError, match="entity declarations"):
        dtm.DocumentToMarkdownConverter().extract_docx_blocks(docx)


def test_ordinary_docx_still_converts(tmp_path: Path) -> None:
    docx = write_docx(tmp_path / "ok.docx", DOCUMENT.format(text="Plain paragraph"))

    _title, blocks = dtm.DocumentToMarkdownConverter().extract_docx_blocks(docx)

    assert [block.text for block in blocks] == ["Plain paragraph"]


@pytest.mark.security
@pytest.mark.parametrize("encoding", ["utf-16", "utf-16-le", "utf-16-be", "utf-32"])
def test_entity_declarations_in_wide_encodings_are_rejected(encoding: str) -> None:
    laughs = (
        f'<?xml version="1.0" encoding="{encoding}"?>'
        '<!DOCTYPE r [<!ENTITY a "aaaa"><!ENTITY b "&a;&a;&a;&a;">]><r>&b;</r>'
    ).encode(encoding)

    with pytest.raises(ValueError, match="entity declarations"):
        dtm.parse_untrusted_xml(laughs)
