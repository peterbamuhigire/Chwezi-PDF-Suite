# Changelog

All notable changes will be documented here. The project follows Semantic Versioning once a
public release line begins.

## Unreleased

### Added

- Transformation audit, target architecture, migration plan, roadmap, risk register, security
  model, dependency assessment, and competitive analysis.
- Initial typed `chwezi_docs` package, conversion registry and planner, capability detection,
  `DocumentSuite` facade, and Typer CLI.
- Non-destructive collision handling, staged output validation, and characterization tests.

### Changed

- Product-facing name is now Chwezi Document Suite.
- Runtime package auto-installation is disabled in transitional launchers.
- Content analysis (sending text previews of unclear PDFs to the AI provider) is now off by
  default everywhere. Opt in with the GUI or web checkbox, or `--content-analysis` on the
  organiser and watch-mode CLIs; `watch_setup.py` asks explicitly.
- Default Anthropic model is `claude-haiku-5-5` at low effort, suited to high-volume
  categorisation.
- Documentation states costs as API-call counts instead of unsourced dollar figures.

### Fixed

- AI categorisation no longer defaults to retired models (`gemini-1.5-flash`, shut down
  2025-09-29; `claude-3-5-sonnet-20240620`, retired 2025-10-28; `deepseek-chat`, deprecated
  2026-07-24). Defaults are now `gemini-3.8-flash`, `claude-haiku-5-5`, and `deepseek-flash`;
  override with `model_name`.
- One unmovable PDF no longer aborts an organiser run or drops the log entries of files already
  moved; failures are reported in `summary["failed"]` and the CLI exits non-zero.
- `organization_log.json` is written atomically; a corrupt log is preserved aside instead of
  crashing every later run. Malformed AI items are discarded rather than crashing after a paid
  API call.
- Watch mode detects browser downloads that arrive by rename (`.crdownload`/`.part` to `.pdf`),
  no longer strands a still-growing file, and records its moves in the organisation log.
- Gibberish-filename detection's random-case check can now fire; batch signing no longer
  re-signs its own `signed/` output; a failed Markdown conversion no longer leaves an empty
  `.md`; LibreOffice conversion has a 180-second timeout.
- Interactive setup no longer crashes on a corrupt settings file or a non-numeric batch delay.
- Legacy root modules now pass the full ruff configuration.

### Security

- AI-suggested categories and filenames are sanitised and confined to the library root before
  any move (blocks `..`, absolute paths, drive letters, reserved device names, and NTFS streams).
- The web interface keeps the API key server-side and never returns it; files are addressed by
  server-issued upload ids, so client-supplied paths can no longer move, delete, read, or sign
  arbitrary files; cross-origin write requests and non-loopback Host headers (DNS rebinding)
  are rejected; idle sessions are evicted after 12 hours along with their uploads.
- DOCX, EPUB and PPTX containers are checked for entry count, entry and total size, and
  compression ratio before reading, reads are capped, and XML entity declarations are refused.
- Setup and smoke-test scripts show only the last four characters of an API key.
- New conversion execution stages output before atomic promotion and does not overwrite input
  files by default.
- Known legacy security risks are explicitly documented; the legacy web interface is not
  production-ready.
