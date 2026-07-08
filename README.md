# pyPDFLibrarianSort

Python tools workspace for practical document and content-processing utilities.

The repository started as a PDF-focused project. It now includes conversion, extraction, organization, and publishing helpers, with a stronger focus on Markdown as the output format for downstream AI use.

## Current Direction

The main conversion tools are:

- `pptx_to_epub.py`: converts PowerPoint files into structured Markdown
- `pdf_to_epub.py`: converts PDF, EPUB, DOCX, and DOC files into structured Markdown

Existing PDF tools still in the repo:

- `organize_batch.py`: AI-assisted PDF organization
- `pdf_signature.py`: PDF signature placement with GUI support
- `watch_organizer.py`: watch-mode PDF organization

## Tool: PowerPoint To Markdown

`pptx_to_epub.py` converts `.pptx` files into Markdown by extracting slide text and preserving slide structure.

What it does:

- extracts text from slide titles, text boxes, and tables
- preserves slide order
- renders nested bullets as nested Markdown lists
- creates one Markdown section per slide
- supports a single PowerPoint file or an entire directory
- includes both GUI and CLI modes

GUI:

```bash
python pptx_to_epub.py
```

CLI:

```bash
python pptx_to_epub.py --input "C:\path\deck.pptx" --output-dir "C:\path\markdown"
python pptx_to_epub.py --input "C:\path\slides" --output-dir "C:\path\markdown"
```

## Tool: Document To Markdown

`pdf_to_epub.py` converts `.pdf`, `.epub`, `.docx`, and legacy `.doc` files into Markdown. Directory mode can process all supported formats in one batch.

What it does:

- extracts readable text from PDF pages
- infers heading levels from font size and emphasis
- extracts DOCX paragraphs, headings, lists, and simple tables
- extracts EPUB spine content in reading order
- converts legacy DOC files through LibreOffice or Microsoft Word when available
- merges wrapped lines into paragraphs
- renders detected lists as Markdown lists
- supports a single document file or an entire directory
- includes both GUI and CLI modes

What it does not do:

- OCR scanned or image-only PDFs
- preserve visual PDF layout exactly

GUI:

```bash
python pdf_to_epub.py
```

CLI:

```bash
python pdf_to_epub.py --input "C:\path\book.pdf" --output-dir "C:\path\markdown"
python pdf_to_epub.py --input "C:\path\library" --output-dir "C:\path\markdown"
```

## Installation

```bash
git clone https://github.com/peterbamuhigire/pyPDFLibrarianSort.git
cd pyPDFLibrarianSort
pip install -r requirements.txt
```

The Markdown converter scripts also auto-install missing Python packages when run directly, so a user can usually start with `python pdf_to_epub.py` or `python pptx_to_epub.py` from a fresh checkout.

Core dependencies for the Markdown converters:

- `python-pptx`
- `pdfplumber`
- `pypdf`

Legacy `.doc` conversion additionally requires either LibreOffice on `PATH` or Microsoft Word. The tool will auto-install `pywin32` when it needs Word automation.

## Documentation

- [Project Brief](PROJECT_BRIEF.md)
- [Project Summary](docs/overview/PROJECT_SUMMARY.md)
- [Quick Start](docs/guides/QUICK_START.md)
- [Getting Started](docs/guides/GET_STARTED.md)
- [Features Summary](docs/features/FEATURES_SUMMARY.md)
- [PowerPoint To EPUB Guide](docs/guides/POWERPOINT_TO_EPUB_GUIDE.md)
- [PDF To EPUB Guide](docs/guides/PDF_TO_EPUB_GUIDE.md)
- [Web Interface Guide](docs/guides/WEB_INTERFACE_GUIDE.md)
- [PDF Signature Guide](docs/guides/SIGNATURE_GUIDE.md)

## Testing

```bash
python test_pptx_to_epub.py
python test_pdf_to_epub.py
python test_signature.py
```

## License

MIT License.
