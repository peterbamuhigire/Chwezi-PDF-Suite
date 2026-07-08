# Document To Markdown Guide

## Purpose

`pdf_to_epub.py` converts PDF, EPUB, DOCX, and DOC documents into Markdown files.

This is useful when you want a cleaner text format that AI tools and documentation workflows can work with directly.

## What Gets Extracted

- document title from PDF metadata when available
- headings inferred from font size and emphasis
- paragraph text with wrapped lines merged back together
- ordered and unordered lists
- simple indented monospace code blocks
- DOCX headings, paragraphs, lists, and simple tables
- EPUB chapters in spine order

## What Gets Ignored

- original PDF page layout
- images and non-text visual content
- OCR for scanned PDFs

## GUI Usage

Run:

```bash
python pdf_to_epub.py
```

Then:

1. choose `Single document file` or `Whole directory of documents`
2. browse to the input file or folder
3. choose the output directory
4. click `Convert to Markdown`

## CLI Usage

Single file:

```bash
python pdf_to_epub.py --input "C:\books\guide.pdf" --output-dir "C:\exports\markdown"
python pdf_to_epub.py --input "C:\books\guide.epub" --output-dir "C:\exports\markdown"
python pdf_to_epub.py --input "C:\books\guide.docx" --output-dir "C:\exports\markdown"
```

Directory mode:

```bash
python pdf_to_epub.py --input "C:\books" --output-dir "C:\exports\markdown"
```

If required Python packages are missing, the tool installs them automatically before conversion starts.

## Output Behavior

- each `.pdf`, `.epub`, `.docx`, or `.doc` produces one `.md`
- when converting a directory, supported files are found recursively and processed in one batch
- relative folder structure is preserved inside the output directory
- if two files would create the same Markdown filename, the second output includes the source extension, such as `book_docx.md`
- the converter tries to infer document headings, paragraphs, lists, and code blocks

## Limitations

- best results come from text-based PDFs
- scanned or image-only PDFs may produce poor output unless OCR is added first
- legacy `.doc` conversion requires LibreOffice on `PATH` or Microsoft Word; `pywin32` is auto-installed when Word automation is needed
- visual formatting is simplified into readable Markdown

## Recommended Validation

```bash
python test_pdf_to_epub.py
```
