# Quick Start

Install the extraction and development dependencies:

```powershell
python -m pip install -e ".[dev,extract]"
```

Launch the suite:

```powershell
python index-app.py
```

Or launch the unified converter directly:

```powershell
python documents_to_markdown.py --gui
```

CLI examples:

```powershell
python documents_to_markdown.py --input "C:\documents\report.pdf" --output-dir "C:\exports\markdown"
python documents_to_markdown.py --input "C:\documents\deck.pptx" --output-dir "C:\exports\markdown"
python documents_to_markdown.py --input "C:\documents" --output-dir "C:\exports\markdown"
```

The directory command accepts mixed PDF, EPUB, Word, and PowerPoint inputs. Output is structured text, not a visual copy of the original document.
