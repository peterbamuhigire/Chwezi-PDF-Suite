"""PyMuPDF stamping must place the signature on every page regardless of page rotation.

PyMuPDF is AGPL-licensed and deliberately not a declared dependency (see
docs/reference/DEPENDENCIES.md), so this test only runs where it is installed.
"""

from io import BytesIO
from pathlib import Path

import pytest

ROTATIONS = [0, 90, 180, 270, 0, 270]


@pytest.mark.integration
def test_signature_lands_in_bottom_left_on_rotated_pages(tmp_path: Path) -> None:
    fitz = pytest.importorskip("fitz")
    if not hasattr(fitz, "Document"):
        pytest.skip("installed 'fitz' module is not PyMuPDF")
    image_module = pytest.importorskip("PIL.Image")
    image_draw = pytest.importorskip("PIL.ImageDraw")
    from pdf_signature import PDFSignature

    signature = image_module.new("RGBA", (200, 80), (0, 0, 0, 0))
    image_draw.Draw(signature).rectangle([0, 0, 199, 79], fill=(200, 30, 30, 220))
    buffer = BytesIO()
    signature.save(buffer, format="PNG")
    signature_path = tmp_path / "signature.png"
    signature_path.write_bytes(buffer.getvalue())

    source_path = tmp_path / "source.pdf"
    output_path = tmp_path / "signed.pdf"
    with fitz.open() as source:
        for rotation in ROTATIONS:
            page = source.new_page(width=595, height=842)
            page.set_rotation(rotation)
            page.insert_text((50, 100), f"Rotation {rotation}", fontsize=24)
        source.save(source_path)

    signer = PDFSignature(
        signature_image_path=str(signature_path),
        position="bottom-left",
        scale=0.15,
        opacity=0.9,
        x_offset=0.3,
        y_offset=0.3,
    )
    total, signed = signer._add_signature_to_pdf_with_pymupdf(str(source_path), str(output_path))
    assert signed == total == len(ROTATIONS)

    with fitz.open(output_path) as document:
        for index, page in enumerate(document):
            rect = page.rect
            clip = fitz.Rect(rect.x0, rect.y1 * 0.80, rect.x1 * 0.25, rect.y1)
            samples = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5), clip=clip).samples
            non_white = sum(
                1
                for offset in range(0, len(samples), 3)
                if not all(channel > 240 for channel in samples[offset : offset + 3])
            )
            assert non_white > 20, f"page {index + 1} (rotation {ROTATIONS[index]}) unsigned"
