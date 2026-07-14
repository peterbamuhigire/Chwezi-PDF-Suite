# Initial Transformation Report

This report is the entry point for the Phase 0 assessment. It maps the requested sections A–I to detailed, evidence-backed documents.

## A. Executive assessment

Chwezi-PDF-Suite is currently a set of capable prototypes. Its distinctive material is structured Markdown extraction, visual signature placement and reviewed AI-assisted organisation. It is prevented from being a professional suite by unsafe path/output handling, misleading naming, runtime installation, duplicated interfaces, absent packaging/tests/CI and an insecure web prototype.

Preserve the conversion heuristics, visual placement semantics, dry-run organisation and review-before-move workflow. Refactor them behind typed application services. Retire or separate the unrelated Git puller, runtime bootstrap and obsolete publishing/setup guidance after migration paths exist.

Evidence: [Current State Audit](../architecture/CURRENT_STATE_AUDIT.md).

## B. Repository map

The significant-file map and responsibilities are in the audit's “Repository map”. The repository contains 23 Python files, with product logic concentrated in five large scripts: `organize_batch.py` (825 lines), `pdf_signature.py` (971), `pdf_to_epub.py` (935), `pptx_to_epub.py` (569) and `web_interface.py` (558).

## C. Current feature matrix

The matrix in the audit marks conversion, organisation, watch, web, signature and interface capabilities as working, partial, absent or security-sensitive. No feature is classified from README claims alone; each entry reflects implementation and executable-script evidence.

## D. Target product definition

Target users are desktop users, automation/CLI users, Python developers and local web users. The first release is an offline-capable modular monolith for Windows 10/11, recent Ubuntu/Debian and recent macOS. Optional office, OCR and remote AI capabilities degrade visibly when absent. Authenticated multi-user server mode is excluded from 1.0.

Value proposition: a privacy-first local document processor that combines PDF operations, structured/AI-ready extraction, safe batch automation and a typed developer API.

## E. Architecture proposal

The component diagram, boundaries, critical flows, job model, trust boundaries, errors and configuration approach are in [Target Architecture](../architecture/TARGET_ARCHITECTURE.md). The governing choice is a modular monolith with process-isolated long jobs, not microservices.

## F. Technology decisions

Proposed decisions are Hatchling, Typer, PySide6, FastAPI, SQLite, pypdf/pikepdf, optional OCRmyPDF/Tesseract, LibreOffice and pyHanko. PyMuPDF remains conditional on an explicit AGPL/commercial distribution decision. These are proposals until numbered ADRs are accepted.

## G. Gap analysis

[Feature Gap Analysis](FEATURE_GAP_ANALYSIS.md) compares the flat scripts with P0/P1/P2 product outcomes and evaluates advanced features without assuming they belong in core.

## H. Phased roadmap

[Implementation Roadmap](IMPLEMENTATION_ROADMAP.md) defines milestones 0.1 through 1.0 with dependencies, relative effort and observable exit criteria. [Risk Register](RISK_REGISTER.md) records the highest threats, owners and triggers.

## I. First implementation sprint

The first sprint is deliberately narrow: packaging, typed domain contracts, capability registry/planner, a safe transitional file-to-Markdown service, three CLI commands, characterisation tests and removal of runtime dependency installation. It does not promise PDF tools, OCR, desktop, jobs or web replacement.

## Decisions awaiting maintainer acceptance

1. Choose the project licence before public package distribution.
2. Accept or revise the proposed desktop/PDF library ADRs.
3. Decide whether `git_puller.py`, embedded skills and the personal category template remain in this product repository.
4. Approve a public/synthetic conversion corpus and performance targets.

