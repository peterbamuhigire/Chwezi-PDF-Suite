"""The `chwezi` command-line interface."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from chwezi_docs.application.capability_service import CapabilityService
from chwezi_docs.domain.errors import ChweziError
from chwezi_docs.domain.formats import DocumentFormat, OverwritePolicy
from chwezi_docs.suite import DocumentSuite
from chwezi_docs.version import __version__

app = typer.Typer(
    name="chwezi",
    help="Chwezi Document Suite: local document conversion and management.",
    no_args_is_help=True,
    add_completion=False,
)


def _emit_error(error: ChweziError, json_output: bool) -> None:
    if json_output:
        typer.echo(json.dumps({"error": error.to_dict()}, ensure_ascii=False))
    else:
        typer.echo(f"{error.code}: {error.message}", err=True)
        if error.detail:
            typer.echo(error.detail, err=True)
        typer.echo(f"Action: {error.suggested_action}", err=True)


@app.command()
def version(
    json_output: Annotated[
        bool, typer.Option("--json", help="Emit machine-readable JSON.")
    ] = False,
) -> None:
    """Show the application version."""
    if json_output:
        typer.echo(json.dumps({"name": "Chwezi Document Suite", "version": __version__}))
    else:
        typer.echo(f"Chwezi Document Suite {__version__}")


@app.command()
def capabilities(
    json_output: Annotated[
        bool, typer.Option("--json", help="Emit machine-readable JSON.")
    ] = False,
) -> None:
    """Show implemented conversion routes and missing optional requirements."""
    reports = CapabilityService().reports()
    if json_output:
        typer.echo(json.dumps({"converters": [report.to_dict() for report in reports]}, indent=2))
        return

    for report in reports:
        state = "available" if report.available else "unavailable"
        typer.echo(
            f"{report.converter.source_format.value:>8} -> "
            f"{report.converter.target_format.value:<9} {state:<11} "
            f"{report.converter.name}"
        )
        for missing in report.missing:
            typer.echo(f"  missing: {missing}")


@app.command()
def convert(
    source: Annotated[Path, typer.Argument(help="One source document to convert.")],
    target: Annotated[str, typer.Option("--to", help="Target format, for example markdown.")],
    output_dir: Annotated[
        Path,
        typer.Option("--output-dir", "--output", help="Directory for generated output."),
    ] = Path("."),
    policy: Annotated[
        OverwritePolicy,
        typer.Option("--policy", help="Collision policy: fail, skip, rename, or overwrite."),
    ] = OverwritePolicy.RENAME,
    json_output: Annotated[
        bool, typer.Option("--json", help="Emit machine-readable JSON.")
    ] = False,
) -> None:
    """Convert one document through the shared conversion service."""
    try:
        result = DocumentSuite().convert(
            source=source,
            target_format=DocumentFormat.parse(target),
            output_dir=output_dir,
            overwrite_policy=policy,
        )
    except (ChweziError, ValueError) as exc:
        error = (
            exc
            if isinstance(exc, ChweziError)
            else ChweziError(
                code="INVALID_ARGUMENT",
                message="A command argument is invalid.",
                detail=str(exc),
                suggested_action="Review `chwezi convert --help` and choose a supported value.",
            )
        )
        _emit_error(error, json_output)
        raise typer.Exit(code=2) from exc

    if json_output:
        typer.echo(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
        return

    for output in result.output_files:
        typer.echo(f"Created: {output}")
    for warning in result.warnings:
        typer.echo(f"Warning [{warning.code}]: {warning.message}")
