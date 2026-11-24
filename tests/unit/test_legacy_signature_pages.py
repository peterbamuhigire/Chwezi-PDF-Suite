import inspect

import pytest

from pdf_signature import PDFSignature


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("2,5", {2, 5}),
        ("2, 5, 7", {2, 5, 7}),
        (" 3 ,", {3}),
        ("1-3,10", {1, 2, 3, 10}),
        ("1 - 3, 10", {1, 2, 3, 10}),
        ("2 5", {2, 5}),
        ("2;5", {2, 5}),
        ("4,4,4", {4}),
    ],
)
def test_parse_page_range_accepts_comma_separated_lists(text, expected):
    assert PDFSignature._parse_page_range(text) == expected


@pytest.mark.parametrize("text", ["abc", "0", "5-2", "2,x", "1-"])
def test_parse_page_range_rejects_invalid_input_with_clear_message(text):
    with pytest.raises(ValueError, match="page"):
        PDFSignature._parse_page_range(text)


def test_default_signature_size_is_eleven_percent():
    default = inspect.signature(PDFSignature.__init__).parameters["scale"].default
    assert default == pytest.approx(0.11)
