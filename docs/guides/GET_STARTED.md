# Getting Started

## Requirements

Use Python 3.11 or newer. Python 3.12 is the primary development version.

```powershell
python -m pip install -e ".[dev,extract]"
```

## Open the document launcher

```powershell
python index-app.py
```

The launcher opens centered and provides the PDF organiser, PDF signer, and unified Documents to Markdown converter.

## Convert documents to Markdown

Open the converter GUI:

```powershell
python documents_to_markdown.py --gui
```

Convert one file from the CLI:

```powershell
python documents_to_markdown.py --input "C:\documents\deck.pptx" --output-dir "C:\exports\markdown"
```

Convert a mixed directory recursively:

```powershell
python documents_to_markdown.py --input "C:\documents" --output-dir "C:\exports\markdown"
```

Supported inputs are `.pdf`, `.epub`, `.docx`, `.doc`, and `.pptx`. See the [conversion guide](DOCUMENTS_TO_MARKDOWN_GUIDE.md) for fidelity limits and collision behavior.

## Verify the converter

```powershell
python test_documents_to_markdown.py
```

For packaged automation, use `chwezi capabilities` before `chwezi convert` so optional parser availability is explicit.
