"""Regression tests for legacy PDF signature batch and logging behaviour."""

import json

import pytest

pytest.importorskip("PIL")
pytest.importorskip("reportlab")
pytest.importorskip("pypdf")

from PIL import Image

from pdf_signature import PDFSignature


@pytest.fixture
def signer(tmp_path):
    image = tmp_path / "sig.png"
    Image.new("RGBA", (40, 20), (0, 0, 0, 255)).save(image)
    return PDFSignature(str(image))


def test_second_batch_run_does_not_resign_output(signer, tmp_path, monkeypatch):
    folder = tmp_path / "pdfs"
    folder.mkdir()
    (folder / "one.pdf").write_bytes(b"%PDF-1.4")
    calls = []

    def fake_sign(input_path, output_path=None):
        calls.append(input_path)
        out = tmp_path / "unused" if output_path is None else output_path
        import os

        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "wb") as handle:
            handle.write(b"%PDF-1.4")
        return {
            "input_path": input_path,
            "output_path": out,
            "success": True,
            "total_pages": 1,
            "pages_signed": 1,
            "error": None,
        }

    monkeypatch.setattr(signer, "add_signature_to_pdf", fake_sign)

    signer.batch_sign_pdfs(str(folder))
    signer.batch_sign_pdfs(str(folder))

    assert len(calls) == 2
    assert all("signed" not in str(c) for c in calls)


def test_output_equal_to_input_is_rejected(signer, tmp_path):
    pdf = tmp_path / "doc.pdf"
    pdf.write_bytes(b"%PDF-1.4 original")

    result = signer.add_signature_to_pdf(str(pdf), str(pdf))

    assert result["success"] is False
    assert "same" in result["error"]
    assert pdf.read_bytes() == b"%PDF-1.4 original"


def test_corrupt_log_is_moved_aside(signer, tmp_path):
    log = tmp_path / "signature_log.json"
    log.write_text("{not json", encoding="utf-8")
    entry = {
        "success": True,
        "input_path": "a",
        "output_path": "b",
        "total_pages": 1,
        "pages_signed": 1,
    }

    signer._write_log([entry], str(log))

    assert len(json.loads(log.read_text(encoding="utf-8"))["signed_files"]) == 1
    backups = list(tmp_path.glob("signature_log.corrupt-*.json"))
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == "{not json"


def test_log_without_signed_files_key_is_tolerated(signer, tmp_path):
    log = tmp_path / "signature_log.json"
    log.write_text("{}", encoding="utf-8")
    entry = {
        "success": True,
        "input_path": "a",
        "output_path": "b",
        "total_pages": 1,
        "pages_signed": 1,
    }

    signer._write_log([entry], str(log))

    assert len(json.loads(log.read_text(encoding="utf-8"))["signed_files"]) == 1
