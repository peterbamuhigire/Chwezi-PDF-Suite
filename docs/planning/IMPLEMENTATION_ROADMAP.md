# Implementation Roadmap

Relative effort uses S/M/L/XL and is not a calendar commitment.

## Release sequence

| Milestone | Scope | Effort | Dependencies | Exit criteria |
|---|---|---:|---|---|
| 0.1 Foundation alpha | package, typed contracts, errors, capability registry/planner, safe file-to-Markdown path, CLI | M | baseline audit | wheel installs; no runtime install; tests pass |
| 0.2 PDF core alpha | merge, split, extract, rotate, reorder, metadata, validation | L | safe filesystem and result contract | semantic PDF corpus passes |
| 0.3 Extraction alpha | Markdown profiles, structured JSON, DOCX/PPTX/EPUB migration, batch results | L | schema ADR and golden files | schema validation and warnings |
| 0.4 Automation beta | SQLite jobs, organisation rules, workflows and recoverable watch | XL | job/event contracts | restart, retry, undo and dry-run tests |
| 0.5 Desktop beta | PySide6 shell, progress/history/settings, initial previews | XL | stable services/jobs | no GUI-thread processing; accessibility baseline |
| 0.6 OCR/signing beta | OCRmyPDF adapter, visual-signature service, signature inspection research | L | worker isolation and dependency probes | scanned/born-digital corpus passes |
| 0.7 Local web beta | FastAPI job API and local UI | L | jobs and secure upload service | localhost security tests and retention |
| 1.0 release candidate | installers, docs, SBOM, three-OS CI, performance corpus | XL | all P0 and selected P1 | release gates pass; limitations published |

## First implementation sprint

Goal: create an independently reviewable foundation without deleting behaviour.

Included:

- PEP 621/Hatchling `pyproject.toml` and `src/chwezi_docs`;
- version, typed domain enums/dataclasses and error hierarchy;
- format capability registry and deterministic direct-path planner;
- `DocumentSuite.convert()` for the existing file-to-Markdown routes through transitional adapters;
- non-destructive collision policy, staging, basic validation and cleanup;
- `chwezi version`, `chwezi capabilities` and `chwezi convert`;
- pytest configuration that excludes interactive legacy scripts;
- characterisation and safety tests;
- removal of import-time dependency installation.

Excluded:

- directory/batch conversion through the new API;
- PDF page tools, OCR, job persistence, desktop/web rewrites;
- cryptographic signing, PDF/A, secure redaction and enterprise mode.

Sprint exit criteria:

1. `pip install -e .` exposes `chwezi`.
2. core import succeeds without cloud, desktop or OCR extras.
3. a source collision never overwrites unless explicitly requested.
4. failed conversion leaves no final placeholder.
5. registry reports unavailable optional requirements honestly.
6. legacy standalone tests still pass.
7. new pytest, Ruff and package build checks pass or gaps are recorded.

## Success measures

Engineering baselines for 1.0:

- at least 85% line coverage for domain/application code;
- zero known critical security findings;
- Windows, Ubuntu and macOS installation checks;
- all public API methods covered by tests;
- failure leaves original and prior output unchanged;
- temporary directories removed after normal success/failure.

Performance budgets will be set only after the representative corpus is checked in or generated. The next milestone must record baseline timings before setting thresholds for 100-page operations, OCR or 500 MB inputs.

