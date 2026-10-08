# Chwezi Document Suite

Chwezi Document Suite is becoming a privacy-first, offline-capable document-processing
platform for desktop users, command-line automation, local web workflows, and Python
integrations. The project is in an early transformation release: its tested foundation and
legacy Markdown converters are available, while the broader PDF, OCR, workflow, desktop, and
web capabilities remain roadmap work.

## What works in this alpha

- A typed `chwezi_docs` Python package and `DocumentSuite` facade
- A `chwezi` CLI with `version`, `capabilities`, and single-file `convert` commands
- Non-destructive output collision policies and staged output promotion
- Capability-aware PDF, DOCX, PPTX, EPUB, and legacy DOC to Markdown routes
- Transitional legacy applications for visual signature placement and document organisation

The conversion routes extract text and structure. They do not promise pixel-perfect layout,
OCR, image preservation, or cryptographic signing. Run `chwezi capabilities` to see which
routes are actually available on the current machine.

## Install for development

Python 3.11 or later is required. Python 3.12 is the primary development version.

```bash
git clone https://github.com/peterbamuhigire/Chwezi-PDF-Suite.git
cd Chwezi-PDF-Suite
python -m pip install -e ".[dev,extract]"
```

Dependencies are never installed silently at application runtime. Optional features report
the missing capability and an explicit installation command.

## Quick start

### Desktop launcher

From the repository root, open the document-tool launcher with:

```bash
python index-app.py
```

The launcher opens centered and provides Documents to Markdown, PDF organiser, and PDF Signer.
Its saved light/dark preference applies to the complete interface and to each maintained GUI.
The startup sequence raises the window once so it does not remain hidden behind another Windows
application.

To open the unified converter without the launcher:

```bash
python documents_to_markdown.py --gui
```

If `index-app.py` exits immediately, verify the desktop dependency and reinstall it if needed:

```bash
python -c "import customtkinter; print(customtkinter.__version__)"
python -m pip install "customtkinter>=5.2.0"
```

If the command remains running but no window is visible, use `Alt+Tab` once and confirm that no
older launcher process is still running in Task Manager. The current launcher maps its window only
after the Tk event loop starts, which avoids the previous invisible-start condition.

### Windows executable suite

The repository contains a locked, manifest-driven PyInstaller workflow that builds the launcher
and its three tools into one distributable folder. Install `uv`, then run:

```powershell
uv sync --locked --extra suite --extra test --group desktop-build
python C:\wamp64\www\chwezi-dev-engine\skills\languages\python-modern-standards\scripts\desktop_suite_packager.py doctor --config packaging\desktop-suite.toml
python C:\wamp64\www\chwezi-dev-engine\skills\languages\python-modern-standards\scripts\desktop_suite_packager.py generate --config packaging\desktop-suite.toml
.\scripts\build-desktop-suite.ps1 -UnsignedDevelopmentBuild -SkipInstaller
```

The development command creates `release/chwezi-document-suite-0.2.0-windows-x64.zip` and a
machine-readable evidence file. Do not publish that unsigned artifact. Public releases require a
repository licence, Authenticode configuration, and Inno Setup. See the
[desktop distribution guide](docs/guides/DESKTOP_DISTRIBUTION.md) for the full workflow and for
instructions on reusing the automation in another Python tools project.

### Command line

```bash
chwezi version
chwezi capabilities
chwezi convert report.pdf --to markdown --output-dir output
```

```python
from pathlib import Path

from chwezi_docs import DocumentSuite

suite = DocumentSuite()
result = suite.convert(
    source=Path("report.docx"),
    target_format="markdown",
    output_dir=Path("output"),
)
print(result.output_files)
```

Existing outputs are renamed by default (`report_1.md`, for example). Use the typed overwrite
policy or CLI `--policy` option only when a different collision policy is intentional.

## Engineering status

The repository transformation began with an evidence-backed baseline rather than a wholesale
rewrite:

- [Initial transformation report](docs/planning/INITIAL_TRANSFORMATION_REPORT.md)
- [Current-state audit](docs/architecture/CURRENT_STATE_AUDIT.md)
- [Target architecture](docs/architecture/TARGET_ARCHITECTURE.md)
- [Implementation roadmap](docs/planning/IMPLEMENTATION_ROADMAP.md)
- [Feature gap analysis](docs/planning/FEATURE_GAP_ANALYSIS.md)
- [Risk register](docs/planning/RISK_REGISTER.md)
- [Security threat model](docs/security/THREAT_MODEL.md)
- [Legacy command migration](docs/migration/LEGACY_COMMANDS.md)

Proposed architectural decisions are recorded under
[`docs/architecture/decisions`](docs/architecture/decisions/README.md). “Proposed” is deliberate:
high-impact choices remain reviewable until implementation evidence supports acceptance.

## Quality checks

```bash
python -m ruff check src tests
python -m mypy src/chwezi_docs
python -m pytest --cov=chwezi_docs
python -m build
python -m twine check dist/*
```

Legacy characterization scripts remain available during migration:

```bash
python test_documents_to_markdown.py
python test_signature.py
```

## Security and privacy

Core processing is local. AI organisation in the PDF organiser is optional and is not private
local processing: by default it sends filenames and PDF metadata (title and author) to your chosen
provider, and only sends text previews of unclear files if you explicitly enable content analysis.
The web interface listens on 127.0.0.1:5000 only, has no authentication, keeps the API key
server-side and rejects cross-origin requests; do not expose it to a network. Default models are
`gemini-3.8-flash`, `claude-haiku-5-5` and `deepseek-flash`.

Report vulnerabilities using the process in [SECURITY.md](SECURITY.md).

## Licensing status

The historical README claimed MIT licensing, but no licence file exists in repository history.
Distribution terms are therefore unresolved. A maintainer must select and add a licence before
the project is published to PyPI or redistributed as an application. See
[dependency governance](docs/reference/DEPENDENCIES.md) for third-party licensing concerns.
