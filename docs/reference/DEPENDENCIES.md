# Dependency Governance

Status: initial assessment, not a release licence opinion  
Registry metadata checked: PyPI on 2026-07-14

## Policy

Core remains small. A dependency enters core only if it is required for imports, typed contracts or the principal CLI. Desktop, web, OCR, office, cloud AI and advanced converters are extras. Runtime code never invokes a package installer.

## Proposed groups

| Group | Candidate packages | Behaviour when absent |
|---|---|---|
| core | `typer`, `pypdf` | CLI/API core unavailable only if installation is incomplete |
| extract | `pdfplumber`, `python-pptx`, `Pillow` | affected conversion routes report missing capability |
| desktop | `PySide6` | `chwezi desktop` unavailable; CLI/SDK continue |
| web | `fastapi`, ASGI server selected later | local web unavailable; other interfaces continue |
| ocr | `ocrmypdf` | OCR routes unavailable; born-digital extraction continues |
| office | no Python requirement for LibreOffice adapter; optional `pywin32` on Windows | legacy Office routes report required executable/platform |
| ai | `anthropic`, `google-genai`, `openai` | remote classifiers absent and disabled; local rules continue |
| signing | `pyHanko` | cryptographic signing unavailable; visual placement remains separate |
| dev/test | `pytest`, `pytest-cov`, `ruff`, `mypy`, `hypothesis`, `pip-audit`, `build`, `twine` | not installed in runtime distributions |

## Current dependency review

| Dependency | Role | Licence metadata / concern | Decision |
|---|---|---|---|
| pypdf | structural PDF and current signature fallback | BSD-3-Clause | retain in core initially |
| pdfplumber | layout-aware PDF text extraction | PyPI licence field absent in query; upstream licence must be checked | extraction extra |
| python-pptx | PPTX parsing | MIT | extraction extra |
| Pillow | image validation/manipulation | MIT-CMU | extraction/signing extra |
| ReportLab | overlay PDF generation | BSD-style publisher text | signing/PDF extra |
| PyMuPDF | rendering and optional stamping | AGPL-3.0 or commercial per PyPI | do not bundle until ADR/licence decision |
| Flask/flask-cors | current web prototype | BSD-3-Clause/MIT | remove when FastAPI adapter replaces prototype |
| watchdog | watch events | Apache-2.0 | watch extra |
| CustomTkinter | current launcher | CC0-1.0 | retire after PySide6 migration |
| cloud SDKs | optional remote classification | MIT/Apache-2.0 | AI extra only; disabled by default |

Version strings above are not pins. A lock file and compatibility CI must establish the release set.

## Candidate review

| Candidate | Maintenance/platform evidence | Licence metadata | Main risk |
|---|---|---|---|
| Typer | current PyPI release supports Python 3.10+ | MIT | Click/Rich dependency compatibility |
| Hatchling | standards build backend, Python 3.10+ | MIT | low; build-only |
| PySide6 | wheels for supported desktop platforms; Python 3.10–3.14 in current metadata | LGPL/GPL choices | LGPL compliance, bundle size |
| FastAPI | Python 3.10+ in current metadata | MIT | server security depends on deployment, not framework alone |
| OCRmyPDF | Python 3.11+; external tools/language data vary by platform | MPL-2.0 | system dependency and temporary-space footprint |
| pikepdf | binary wheels and qpdf-based operations | MPL-2.0 | wheel/platform compatibility and API overlap |
| pyHanko | current PDF signing library | MIT | certificate/trust UX and dependency depth |
| Docling | broad structured extraction | check complete transitive/model licences before adoption | large ML/runtime footprint |
| Pandoc | mature standalone converter | GPL executable; subprocess integration/legal review required | binary distribution and templates |

## System dependencies

| Tool | Intended use | Detection | Absence behaviour |
|---|---|---|---|
| LibreOffice/`soffice` | office conversion | executable path plus version probe | office routes unavailable or lower-fidelity parser route used |
| Tesseract/tessdata | OCR languages | OCR adapter probe | language-specific OCR unavailable |
| Ghostscript | selected PDF/A/compression fallback | explicit executable/version probe | affected backend omitted from planner |
| qpdf | validation, encryption and repair adapter | explicit probe | related operations use another validated backend or report unavailable |
| veraPDF | PDF/A validation | explicit probe | no PDF/A conformance claim |
| Poppler | optional render/extract tools | explicit probe | renderer-specific routes unavailable |
| Microsoft Word COM | Windows legacy DOC conversion | OS + COM capability | route unavailable off Windows or without Word |
| Pandoc | rich text conversion | executable/version probe | planner selects another route or reports unavailable |
| Java | only if veraPDF/selected adapters require it | executable/version probe | dependent capability unavailable; never core |

## Package name check

`https://pypi.org/pypi/chwezi-document-suite/json` returned HTTP 404 on 2026-07-14. This means no public project was returned at that time; it does not reserve the name or guarantee PyPI approval. Name ownership must be confirmed during release preparation.

## Release gates

- lock and hash the supported dependency set;
- run `pip-audit` and resolve or document every finding;
- record licence/source/binary redistribution obligations in `THIRD_PARTY_NOTICES.md`;
- test a clean core install and every supported extra independently;
- verify package and import names to prevent dependency confusion;
- never bundle binaries, fonts, icons, certificates or OCR data without redistribution evidence.

The 2026-07-14 workstation audit found vulnerable older environment packages, including
`pypdf` 6.10.2 and Pillow 12.2.0. The package floors are therefore `pypdf>=6.13.3` and
`pillow>=12.3`; findings in unrelated globally installed packages are not evidence about a
clean Chwezi installation and must be re-audited in an isolated release environment.
