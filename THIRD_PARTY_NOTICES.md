# Third-Party Notices

This file is an audit record, not a substitute for the licence texts required by a release.
Chwezi Document Suite does not currently bundle third-party binaries, fonts, OCR language data,
or icons.

Core and proposed optional dependencies include Typer (MIT), pypdf (BSD-3-Clause), pdfplumber
(MIT), python-pptx (MIT), Pillow (HPND), ReportLab (BSD), FastAPI (MIT), PySide6
(LGPL-3.0/GPL/commercial options), OCRmyPDF (MPL-2.0), pikepdf (MPL-2.0), and pyHanko (MIT).
Exact transitive dependencies and notices must be generated from the locked release environment.

LibreOffice, Tesseract, Ghostscript, qpdf, veraPDF, Poppler, Microsoft Word, and Pandoc are
external system integrations. Their executable, data, and redistribution terms must be assessed
separately before bundling. PyMuPDF is not approved as a default distributable dependency until
its AGPL/commercial licensing implications are deliberately resolved.

No release may ship until dependency versions, licences, attribution obligations, source-offer
requirements, and binary redistribution rights have been verified. See
[`docs/reference/DEPENDENCIES.md`](docs/reference/DEPENDENCIES.md).
