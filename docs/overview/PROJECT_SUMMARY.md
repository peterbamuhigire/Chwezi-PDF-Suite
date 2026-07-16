# Chwezi Document Suite Summary

## Scope

This repository is a document-management and manipulation suite. Its working prototypes cover structured Markdown extraction, PDF organisation, watched folders, and visual PDF signature placement. The typed `chwezi_docs` package is gradually replacing direct script-to-script coupling.

## Current tools

| Tool | Responsibility |
| --- | --- |
| `documents_to_markdown.py` | GUI and CLI conversion of PDF, EPUB, DOCX, DOC, and PPTX to Markdown |
| `organize_batch.py` | AI-assisted PDF categorisation and renaming |
| `watch_organizer.py` | Watched-folder PDF organisation |
| `pdf_signature.py` | Visual signature placement in PDF files |
| `index-app.py` | Centered launcher for the document tools |
| `chwezi` | Packaged capability, conversion, and diagnostic commands |

PowerPoint extraction is part of the general Markdown converter. It preserves deck and slide titles, text, bullets, and simple tables while omitting images, charts, notes, animations, and exact layout.

## Documentation

- [Getting started](../guides/GET_STARTED.md)
- [Documents to Markdown](../guides/DOCUMENTS_TO_MARKDOWN_GUIDE.md)
- [Current-state audit](../architecture/CURRENT_STATE_AUDIT.md)
- [Target architecture](../architecture/TARGET_ARCHITECTURE.md)
- [Implementation roadmap](../planning/IMPLEMENTATION_ROADMAP.md)
