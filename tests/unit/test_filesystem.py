from pathlib import Path

import pytest

from chwezi_docs.domain.errors import InvalidDocumentError, OutputCollisionError
from chwezi_docs.domain.formats import OverwritePolicy
from chwezi_docs.infrastructure.filesystem import select_output_path, validate_text_output


def test_default_rename_preserves_existing_output(tmp_path: Path) -> None:
    original = tmp_path / "report.md"
    original.write_text("existing", encoding="utf-8")

    selected, skipped = select_output_path(original, OverwritePolicy.RENAME)

    assert selected == tmp_path / "report_1.md"
    assert not skipped
    assert original.read_text(encoding="utf-8") == "existing"


def test_fail_policy_reports_collision(tmp_path: Path) -> None:
    output = tmp_path / "report.md"
    output.write_text("existing", encoding="utf-8")

    with pytest.raises(OutputCollisionError):
        select_output_path(output, OverwritePolicy.FAIL)


def test_empty_text_output_is_invalid(tmp_path: Path) -> None:
    output = tmp_path / "empty.md"
    output.write_text("  \n", encoding="utf-8")

    with pytest.raises(InvalidDocumentError):
        validate_text_output(output)


def test_skip_and_overwrite_policies_preserve_requested_path(tmp_path: Path) -> None:
    output = tmp_path / "report.md"
    output.write_text("existing", encoding="utf-8")

    assert select_output_path(output, OverwritePolicy.SKIP) == (output, True)
    assert select_output_path(output, OverwritePolicy.OVERWRITE) == (output, False)


def test_missing_or_non_utf8_output_is_invalid(tmp_path: Path) -> None:
    with pytest.raises(InvalidDocumentError):
        validate_text_output(tmp_path / "missing.md")

    binary = tmp_path / "binary.md"
    binary.write_bytes(b"\xff\xfe")
    with pytest.raises(InvalidDocumentError):
        validate_text_output(binary)
