# Documents to Markdown Guide

`documents_to_markdown.py` is the single legacy GUI and CLI for extracting structured Markdown from supported documents. It accepts PDF, EPUB, DOCX, legacy DOC, and PowerPoint PPTX files in one workflow.

## Start the GUI

```powershell
python documents_to_markdown.py --gui
```

The same screen accepts one file or recursively scans a directory. Directory output preserves relative subdirectories. When two source files in the same directory share a stem, the converter adds the source extension, such as `brief_pptx.md`, to avoid overwriting `brief.md`.

## Use the CLI

Single file:

```powershell
python documents_to_markdown.py --input "C:\documents\brief.pptx" --output-dir "C:\exports\markdown"
```

Mixed directory:

```powershell
python documents_to_markdown.py --input "C:\documents" --output-dir "C:\exports\markdown"
```

The packaged command supports one file at a time:

```powershell
chwezi convert "C:\documents\report.docx" --to markdown --output-dir "C:\exports\markdown"
```

## Extraction behavior

| Input | Preserved | Known omissions or limits |
| --- | --- | --- |
| PDF | inferred title, headings, paragraphs, lists, basic code blocks | scanned pages without OCR, images, precise layout, complex tables |
| DOCX | headings, paragraphs, basic lists and tables | advanced styles, drawings, comments, tracked changes |
| DOC | content converted through LibreOffice or Word automation | requires a local office converter; platform-dependent |
| EPUB | spine order, headings, paragraphs, lists, preformatted text | styling, media, interactive content |
| PPTX | deck title, slide boundaries, text, nested bullets, simple tables | images, charts, speaker notes, animations, exact placement |

All routes are intentionally lossy text extraction. The generated Markdown is for reading, search, AI ingestion, and documentation workflows; it is not a visual replica of the source.

## Batch failures

Directory conversion processes smaller files first. A failed file is skipped and reported in the activity log while remaining files continue. The current legacy script can leave an empty output for a failed item because it creates the path before extraction; the packaged `chwezi convert` path stages output before promotion and is safer for single-file automation.

## Characterisation check

```powershell
python test_documents_to_markdown.py
```

The script covers PDF, DOCX, EPUB, PPTX, mixed-format directories, and same-stem output collisions.
