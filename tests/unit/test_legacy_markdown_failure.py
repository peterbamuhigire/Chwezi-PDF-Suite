"""Regression tests for failed conversions in documents_to_markdown."""

import subprocess

import pytest

pytest.importorskip("pdfplumber")
pytest.importorskip("pptx")
pytest.importorskip("pypdf")

import documents_to_markdown as d2m


def _converter(tmp_path):
    return d2m.DocumentToMarkdownConverter()


def test_failed_conversion_leaves_no_empty_output(tmp_path, monkeypatch):
    source = tmp_path / "in" / "bad.docx"
    source.parent.mkdir()
    source.write_bytes(b"not a real docx")
    out = tmp_path / "out"

    converter = _converter(tmp_path)
    results = converter.convert(source, out)

    assert results == []
    assert not (out / "bad.md").exists()


def test_soffice_timeout_is_reported(tmp_path, monkeypatch):
    monkeypatch.setattr(d2m.shutil, "which", lambda _name: "soffice")
    seen = {}

    def fake_run(*_args, **kwargs):
        seen.update(kwargs)
        raise subprocess.TimeoutExpired(cmd="soffice", timeout=kwargs.get("timeout"))

    monkeypatch.setattr(d2m.subprocess, "run", fake_run)
    doc = tmp_path / "old.doc"
    doc.write_bytes(b"x")

    with pytest.raises(RuntimeError, match="timed out"):
        _converter(tmp_path)._convert_legacy_doc_to_docx(doc, tmp_path)

    assert seen["timeout"] == 180
