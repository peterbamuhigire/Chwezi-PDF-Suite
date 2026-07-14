import json
from pathlib import Path

from typer.testing import CliRunner

from chwezi_docs.domain.jobs import JobStatus
from chwezi_docs.domain.results import ConversionResult
from chwezi_docs.interfaces.cli.main import app
from chwezi_docs.version import __version__

runner = CliRunner()


def test_version_json_is_machine_readable() -> None:
    result = runner.invoke(app, ["version", "--json"])

    assert result.exit_code == 0
    assert json.loads(result.stdout) == {
        "name": "Chwezi Document Suite",
        "version": __version__,
    }


def test_capabilities_json_has_no_decorative_prefix() -> None:
    result = runner.invoke(app, ["capabilities", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["converters"]
    assert {"source_format", "target_format", "available"} <= payload["converters"][0].keys()


def test_human_version_and_capabilities_are_readable() -> None:
    version_result = runner.invoke(app, ["version"])
    capabilities_result = runner.invoke(app, ["capabilities"])

    assert version_result.exit_code == 0
    assert "Chwezi Document Suite" in version_result.stdout
    assert capabilities_result.exit_code == 0
    assert "markdown" in capabilities_result.stdout


def test_invalid_target_returns_machine_readable_error() -> None:
    result = runner.invoke(app, ["convert", "input.pdf", "--to", "nonsense", "--json"])

    assert result.exit_code == 2
    payload = json.loads(result.stdout)
    assert payload["error"]["code"] == "INVALID_ARGUMENT"


def test_convert_json_uses_shared_suite(monkeypatch, tmp_path: Path) -> None:
    source = tmp_path / "input.pdf"
    source.write_bytes(b"%PDF fixture")
    output = tmp_path / "input.md"
    output.write_text("converted", encoding="utf-8")

    def fake_convert(*args, **kwargs) -> ConversionResult:
        return ConversionResult(
            status=JobStatus.COMPLETED,
            source=source,
            output_files=(output,),
            warnings=(),
            backends=("test",),
            duration_seconds=0.1,
        )

    monkeypatch.setattr("chwezi_docs.interfaces.cli.main.DocumentSuite.convert", fake_convert)
    result = runner.invoke(app, ["convert", str(source), "--to", "markdown", "--json"])

    assert result.exit_code == 0
    assert json.loads(result.stdout)["output_files"] == [str(output)]
