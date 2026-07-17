# Chwezi Document Suite Project Brief

## Product boundary

Chwezi Document Suite is a local-first Python toolkit for document management and manipulation. The repository covers document conversion and extraction, PDF organisation, watched-folder workflows, and visual PDF signature placement. General developer utilities belong in separate tool suites.

## Current entry points

| Job | Entry point |
| --- | --- |
| Convert documents to Markdown | `documents_to_markdown.py` or `chwezi convert` |
| Organise PDF collections | `organize_batch.py` |
| Run the organiser web UI | `web_interface.py` |
| Place visual PDF signatures | `pdf_signature.py` |
| Configure watched folders | `watch_setup.py` |
| Open the desktop launcher | `index-app.py` |
| Build the Windows executable suite | `scripts/build-desktop-suite.ps1` |

The unified Markdown converter accepts PDF, EPUB, DOCX, DOC, and PPTX. PPTX is no longer a separate application.
The Windows suite packages the launcher as `ChweziDocumentSuite.exe` with sibling
`ChweziOrganizer.exe`, `ChweziSigner.exe`, and `ChweziMarkdown.exe` applications. The launcher
resolves these sibling executables when frozen and launches the Python scripts during development.

## Product rules

- Keep processing local unless the user explicitly configures a remote AI organisation provider.
- Preserve source files by default and make overwrites explicit.
- Report lossy extraction limits; Markdown conversion does not reproduce visual layout.
- Add future utilities only when they manage, inspect, convert, organise, sign, or otherwise manipulate documents.

## Near-term direction

1. Move remaining standalone scripts behind the typed `chwezi_docs` application services.
2. Replace runtime dependency installation with capability checks.
3. Expand conversion validation, OCR, archive safety, and golden-file coverage.
4. Replace prototype interfaces with one desktop document workspace.

See [README.md](README.md), [the implementation roadmap](docs/planning/IMPLEMENTATION_ROADMAP.md), and [the documents-to-Markdown guide](docs/guides/DOCUMENTS_TO_MARKDOWN_GUIDE.md).
