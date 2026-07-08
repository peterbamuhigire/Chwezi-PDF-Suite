# PowerPoint To Markdown Guide

## Purpose

`pptx_to_epub.py` converts PowerPoint presentations into Markdown files by extracting text from slides and preserving their structure.

This is useful when you want structured text that AI tools and documentation workflows can read cleanly.

## What Gets Extracted

- slide titles
- text boxes
- table cell text
- nested bullet levels
- paragraph content in slide order

## What Gets Ignored

- images
- decorative shapes without text
- non-text visual content

## GUI Usage

Run:

```bash
python pptx_to_epub.py
```

Then:

1. choose `Single PowerPoint file` or `Whole directory of PowerPoint files`
2. browse to the input file or folder
3. choose the output directory
4. click `Convert to Markdown`

## CLI Usage

Single file:

```bash
python pptx_to_epub.py --input "C:\slides\deck.pptx" --output-dir "C:\exports\markdown"
```

Directory mode:

```bash
python pptx_to_epub.py --input "C:\slides" --output-dir "C:\exports\markdown"
```

If `python-pptx` is missing, the tool installs it automatically before conversion starts.

## Output Behavior

- each `.pptx` produces one `.md`
- when converting a directory, `.pptx` files are found recursively
- relative folder structure is preserved inside the output directory
- slide order is preserved in the Markdown output

## Markdown Structure

For each presentation:

- the presentation becomes one Markdown file
- each slide becomes one section
- slide titles are used as section headings where available
- nested bullets are rendered as nested lists
- slides without extractable text get a placeholder note

## Limitations

- supports `.pptx` files, not legacy `.ppt`
- image text is not OCR'd
- visual slide layout is not reproduced

## Recommended Validation

```bash
python test_pptx_to_epub.py
```
