# Smart Renaming Guide

This guide documents a PDF-specific renaming workflow inside the Chwezi Document Suite.

## How the System Handles Gibberish Filenames

The PDF organiser now includes **intelligent content analysis** to handle PDFs with meaningless filenames like `SAJSABC4345.pdf`.

## How It Works

### 1. **Gibberish Detection**

The system automatically detects gibberish filenames by checking:

- **Too short**: Less than 5 characters
- **Mostly numbers**: More than 60% digits (e.g., `12345678.pdf`)
- **All numbers**: Only numbers (e.g., `987654321.pdf`)
- **Random case mixing**: Weird patterns (e.g., `aBcDeF123.pdf`)
- **Temp file patterns**: Starts with `temp`, `tmp`, `download`, `untitled`
- **No vowels**: No vowels in the name (e.g., `XCVBNM.pdf`)

If **2 or more** of these checks pass, the filename is considered gibberish.

### 2. **Content Extraction**

When a gibberish filename is detected, the system:

1. **Extracts PDF metadata** (title, author, subject)
2. **Reads the first 3 pages** of actual text content
3. **Sends to AI** along with the category structure

### 3. **AI Analysis**

The AI receives:

```
Filename: SAJSABC4345.pdf (gibberish detected)
Metadata Title: A Study of Eastern Rabbits
Content Preview: "This research paper examines the behavioral patterns of
                 eastern rabbit populations in North America..."
```

The AI then:
- **Categorizes** based on content: `Science/Biology/Zoology`
- **Suggests rename**: `A Study of Eastern Rabbits.pdf`

### 4. **Result**

```
Original: SAJSABC4345.pdf
Renamed:  A Study of Eastern Rabbits.pdf
Category: Science/Biology/Zoology
```

## Examples

### Example 1: Gibberish with Good Metadata

```
Input:
  Filename: XYZ123456.pdf
  Metadata: "Python Machine Learning: A Comprehensive Guide"
  Author: John Smith

Output:
  Renamed: Python Machine Learning - A Comprehensive Guide.pdf
  Category: Computer & ICT/Programming/Python
```

### Example 2: Gibberish with No Metadata

```
Input:
  Filename: temp_download_987.pdf
  Metadata: (empty)
  Content: "Introduction to Quantum Physics. Chapter 1: Wave-Particle Duality..."

Output:
  Renamed: Introduction to Quantum Physics.pdf
  Category: Science/Physics/Quantum Mechanics
```

### Example 3: Already Good Filename

```
Input:
  Filename: Eastern Rabbit Behavior Study 2024.pdf
  Metadata: "A Study of Eastern Rabbits"

Output:
  Renamed: (no change - filename already descriptive)
  Category: Science/Biology/Zoology
```

## Cost Impact

**Content analysis adds minimal cost:**

- Extracts ~1000 characters per PDF
- Still uses batch processing: previews ride in the same single API call
- Example: 50 PDFs with gibberish names = **one API call** (vs 50 calls without batching); the previews add input tokens, so the call costs somewhat more
- Off by default: enable it explicitly, because previews of document text leave your computer

The extra content is worth it for proper categorization!

## How to Use

### Batch Mode (Content Analysis must be enabled)

```bash
python organize_batch.py --content-analysis
```

Content analysis is **off by default** everywhere. Enable it explicitly:

- Desktop GUI: tick **Send text previews of unclear files to the AI provider**.
- Web interface: tick the same option in Settings.
- Watch mode: pass `--content-analysis`.
- CLI: pass `--content-analysis` to `organize_batch.py`.

Without it, only filenames and PDF metadata (title and author) are sent to the AI provider. With it, a text preview (about 1000 characters from the first pages) of files with unclear names is also sent.

### Watch Mode (Auto-Rename Gibberish)

```bash
python watch_organizer.py --ebooks F:/ebooks --provider gemini --api-key YOUR_KEY --content-analysis
```

With `--content-analysis`, watch mode automatically:
1. Detects gibberish filenames
2. Reads content
3. Suggests better names
4. Renames and organizes

### Test Content Analyzer

```bash
python pdf_content_analyzer.py "path/to/SAJSABC4345.pdf"
```

Output:
```
====================================================================
PDF Content Analysis
====================================================================

Filename: SAJSABC4345.pdf
Is Gibberish: True
Gibberish Indicators:
  ✓ mostly_numbers
  ✓ no_vowels
  ✓ random_case_mix

Metadata:
  title: A Study of Eastern Rabbits
  author: Dr. Jane Smith

Content Preview (45 total pages):
This research paper examines the behavioral patterns of eastern
rabbit populations in North America. Our five-year longitudinal
study reveals...
====================================================================
```

## Configuration

### Content Analysis in Code

Content analysis is opt-in. Pass `use_content_analysis=True` to enable it (the default sends only filenames and metadata):

```python
from organize_batch import BatchPDFOrganizer

organizer = BatchPDFOrganizer(
    downloads_folder="~/Downloads",
    ebooks_folder="~/ebooks",
    api_key="YOUR_KEY",
    use_content_analysis=True  # Opt in: send text previews of unclear files
)
```

### Adjust Content Extraction

```python
from pdf_content_analyzer import PDFContentAnalyzer

analyzer = PDFContentAnalyzer(
    max_pages=5,      # Read up to 5 pages (default: 3)
    max_chars=3000    # Extract up to 3000 chars (default: 2000)
)
```

## What Gets Renamed?

The system renames PDFs when:

1. **Filename is gibberish** (detected automatically)
2. **Metadata has a better title** (uses that)
3. **Content reveals a clear title** (AI suggests one)

The system **does NOT** rename:

1. Already descriptive filenames
2. When no better alternative exists
3. When content is unclear

## Manual Override

If you want to keep the original gibberish filename:

Before organizing, the system shows a summary:

```
FILE RENAMES (5 files):
  'XYZ123456.pdf' → 'Python Machine Learning Guide.pdf'
  'ABCD789.pdf' → 'Quantum Physics Introduction.pdf'
  ...

Proceed with moving and renaming these files? (y/n):
```

Just press `n` to cancel if you don't like the suggested names.

## Best Practices

1. **Let the AI help**: Gibberish filenames get much better names
2. **Check the preview**: Review renames before approving
3. **Use good source PDFs**: PDFs with embedded metadata work best
4. **Trust the content analysis**: The first few pages usually reveal the topic

## Troubleshooting

### "No content extracted"
- PDF might be scanned images (no text)
- Solution: Use OCR or manually rename

### "Wrong rename suggested"
- Content might be misleading (e.g., cover page vs. actual content)
- Solution: Review and reject rename, or manually rename after

### "Takes longer than before"
- Content extraction adds processing time
- Solution: Still worth it for proper organization!

## Summary

**Before Smart Renaming:**
```
SAJSABC4345.pdf → Uncategorized/SAJSABC4345.pdf
```

**After Smart Renaming:**
```
SAJSABC4345.pdf → Science/Biology/Zoology/A Study of Eastern Rabbits.pdf
```

Much better! 🎉
