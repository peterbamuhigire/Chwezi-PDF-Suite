# PDF Signature Guide

This guide documents one PDF-specific tool inside the Chwezi Document Suite.

Complete guide to signing PDFs with the Chwezi Document Suite.

## Overview

The PDF Signature Tool lets you add PNG signature images to PDFs with extensive configuration options. **No AI credits required** - pure PDF manipulation.

## Quick Start

### Web Interface (Recommended)

1. **Start the web interface:**
   ```bash
   python web_interface.py
   ```

2. **Navigate to Sign PDFs:**
   - Click "✍️ Sign PDFs" in the header

3. **Upload your signature:**
   - Drag & drop a PNG signature image
   - Or click to browse

4. **Configure signature:**
   - Choose pages to sign (all, first, last, odd, even, or custom range)
   - Select position (4 corners available)
   - Adjust size (10-100% of A4 portrait width)
   - Set margins (0.1-2.0 inches from edges)
   - Configure opacity (10-100%)
   - Set rotation (0-360 degrees)
   - Preview updates in real-time

5. **Upload PDFs:**
   - Drag & drop PDFs to sign
   - Or click to browse

6. **Sign:**
   - Click "✍️ Sign PDFs"
   - Download signed PDFs individually

### Interactive CLI

```bash
python sign_setup.py
```

Follow the step-by-step wizard:
1. Select signature PNG
2. Choose PDFs (single or directory)
3. Configure output location
4. Select pages to sign
5. Choose position
6. Set size, margins, opacity, rotation
7. Review configuration
8. Sign PDFs

### Direct CLI (for scripting)

```bash
# Basic usage
python pdf_signature.py --signature sig.png --input document.pdf

# All PDFs in directory
python pdf_signature.py --signature sig.png --input docs/ --output signed/

# Custom configuration
python pdf_signature.py --signature sig.png --input doc.pdf \
    --position top-right \
    --scale 0.2 \
    --pages "1,3,5-10" \
    --opacity 0.8 \
    --rotation 15
```

## Features

### Page Selection

Sign specific pages or page ranges:

- **All pages**: `--pages all`
- **First page only**: `--pages first`
- **Last page only**: `--pages last`
- **Odd pages**: `--pages odd`
- **Even pages**: `--pages even`
- **Custom range**: `--pages "1-5,10,15-20"`

**Examples:**
```bash
# Sign only first page
python pdf_signature.py --signature sig.png --input doc.pdf --pages first

# Sign odd pages
python pdf_signature.py --signature sig.png --input doc.pdf --pages odd

# Sign specific pages
python pdf_signature.py --signature sig.png --input doc.pdf --pages "1,3,5-10"
```

### Position Options

Four corner positions available:

```
┌─────────────────┐
│ 3           4   │ (3 = top-left, 4 = top-right)
│                 │
│                 │
│ 1           2   │ (1 = bottom-left, 2 = bottom-right)
└─────────────────┘
```

**Default:** bottom-right

**Examples:**
```bash
# Top-right corner
python pdf_signature.py --signature sig.png --input doc.pdf --position top-right

# Bottom-left corner
python pdf_signature.py --signature sig.png --input doc.pdf --position bottom-left
```

### Size Control

Signature size as percentage of A4 portrait width (10-100%):

- **Default:** 25% (0.25)
- **Small:** 15-20%
- **Medium:** 25-35%
- **Large:** 40-50%

**Examples:**
```bash
# Small signature (15% of A4 portrait width)
python pdf_signature.py --signature sig.png --input doc.pdf --scale 0.15

# Large signature (50% of A4 portrait width)
python pdf_signature.py --signature sig.png --input doc.pdf --scale 0.5
```

### Margin Configuration

Distance from page edges in inches (0.1-2.0):

- **X offset:** Horizontal margin from edge
- **Y offset:** Vertical margin from edge
- **Default:** 0.5 inches for both

**Examples:**
```bash
# Close to edges (0.2 inches)
python pdf_signature.py --signature sig.png --input doc.pdf --x-offset 0.2 --y-offset 0.2

# Far from edges (1.5 inches)
python pdf_signature.py --signature sig.png --input doc.pdf --x-offset 1.5 --y-offset 1.5
```

### Opacity Control

Signature transparency (10-100%):

- **100%:** Fully opaque (default)
- **50%:** Semi-transparent
- **10%:** Very transparent

Preserves PNG transparency and adds additional opacity layer.

**Examples:**
```bash
# Semi-transparent signature
python pdf_signature.py --signature sig.png --input doc.pdf --opacity 0.5

# Very transparent watermark
python pdf_signature.py --signature sig.png --input doc.pdf --opacity 0.2
```

### Rotation

Rotate signature 0-360 degrees:

- **0°:** No rotation (default)
- **90°:** Rotated right
- **180°:** Upside down
- **270°:** Rotated left

**Examples:**
```bash
# Rotated 15 degrees
python pdf_signature.py --signature sig.png --input doc.pdf --rotation 15

# Rotated 90 degrees
python pdf_signature.py --signature sig.png --input doc.pdf --rotation 90
```

## Advanced Usage

### Batch Processing

Sign all PDFs in a directory:

```bash
python pdf_signature.py --signature sig.png --input /path/to/pdfs/ --output /path/to/signed/
```

Output structure preserves subdirectories.

### Complex Configurations

Combine all options:

```bash
python pdf_signature.py \
    --signature company_seal.png \
    --input contracts/ \
    --output signed_contracts/ \
    --pages "1,last" \
    --position bottom-right \
    --scale 0.2 \
    --x-offset 0.75 \
    --y-offset 0.5 \
    --opacity 0.9 \
    --rotation 10
```

This signs:
- All PDFs in `contracts/` directory
- Only first and last pages
- Bottom-right corner
- 20% of A4 portrait width
- 0.75" from right edge, 0.5" from bottom
- 90% opacity
- Rotated 10 degrees

### Quiet Mode

Suppress progress output for scripting:

```bash
python pdf_signature.py --signature sig.png --input doc.pdf --quiet
```

## Use Cases

### Legal Documents

Sign first page of contracts:

```bash
python pdf_signature.py \
    --signature signature.png \
    --input contracts/ \
    --pages first \
    --position bottom-right \
    --scale 0.25
```

### Official Stamps

Add company seal to all pages:

```bash
python pdf_signature.py \
    --signature company_seal.png \
    --input reports/ \
    --pages all \
    --position top-right \
    --scale 0.15 \
    --opacity 0.8
```

### Watermarks

Add semi-transparent watermark:

```bash
python pdf_signature.py \
    --signature watermark.png \
    --input documents/ \
    --pages all \
    --position bottom-left \
    --scale 0.3 \
    --opacity 0.3
```

### Certificate Signatures

Sign last page of certificates:

```bash
python pdf_signature.py \
    --signature signature.png \
    --input certificates/ \
    --pages last \
    --position bottom-right \
    --scale 0.3
```

## Troubleshooting

### Signature Not Appearing

**Problem:** Signature doesn't show in signed PDF

**Solutions:**
- Verify PNG image is valid and readable
- Check opacity is not too low (> 0.1)
- Ensure scale is reasonable (0.1-0.5)
- Verify pages selection matches PDF page count

### Signature Too Large/Small

**Problem:** Signature doesn't fit well on page

**Solutions:**
- Adjust `--scale` parameter (0.1-1.0)
- Default 0.25 (25%) works for most cases
- For small signatures: 0.15-0.20
- For large signatures: 0.4-0.5

### Position Issues

**Problem:** Signature appears in wrong location

**Solutions:**
- Check position parameter (bottom-right, bottom-left, top-right, top-left)
- Adjust X/Y offsets (margins from edges)
- Preview in web interface for visual feedback

### Encrypted PDFs

**Problem:** Cannot sign password-protected PDFs

**Solution:** Remove password protection first:
```bash
# Use a tool like qpdf to decrypt
qpdf --decrypt --password=PASSWORD input.pdf decrypted.pdf
python pdf_signature.py --signature sig.png --input decrypted.pdf
```

### Memory Issues

**Problem:** Out of memory with large batches

**Solution:** Process in smaller chunks:
```bash
# Process 50 PDFs at a time
for dir in batch_*; do
    python pdf_signature.py --signature sig.png --input "$dir" --output "signed/$dir"
done
```

## Tips & Best Practices

### Signature Image Preparation

1. **Format:** Always use PNG with transparency
2. **Size:** 400-800px wide is ideal
3. **Resolution:** 300 DPI for print quality
4. **Background:** Transparent for best results
5. **Colors:** Dark colors work better than light

### Creating Transparent PNGs

**Using GIMP:**
1. Open your signature image
2. Layer → Transparency → Add Alpha Channel
3. Use eraser tool to remove background
4. Export as PNG with transparency

**Using Photoshop:**
1. Open image
2. Select background with Magic Wand
3. Delete background
4. Save As → PNG-24 with transparency

### Page Selection Strategy

- **Contracts:** First page only
- **Reports:** All pages or first + last
- **Certificates:** Last page only
- **Invoices:** First page only
- **Multi-party docs:** Specific page ranges

### Position Guidelines

- **Legal signatures:** Bottom-right (traditional)
- **Company seals:** Top-right or top-left
- **Watermarks:** Centered or bottom-left
- **Approvals:** Bottom-right

### Size Recommendations

- **Personal signatures:** 20-30% of A4 portrait width
- **Company seals:** 10-20% of A4 portrait width
- **Watermarks:** 30-50% of A4 portrait width (low opacity)
- **Initials:** 10-15% of A4 portrait width

## Logging

All signature operations are logged to `signature_log.json` in the output directory:

```json
{
  "signed_files": [
    {
      "timestamp": "2026-01-31T10:00:00",
      "input_path": "document.pdf",
      "output_path": "signed/document.pdf",
      "signature": "signature.png",
      "pages_filter": "all",
      "position": "bottom-right",
      "scale": 0.25,
      "x_offset": 0.5,
      "y_offset": 0.5,
      "opacity": 1.0,
      "rotation": 0,
      "total_pages": 10,
      "pages_signed": 10,
      "success": true
    }
  ]
}
```

## Command Reference

### Interactive Setup

```bash
python sign_setup.py
```

### Batch CLI

```bash
python pdf_signature.py [OPTIONS]

Required:
  --signature PATH      PNG signature image
  --input PATH          PDF file or directory

Optional:
  --output PATH         Output file/directory
  --pages OPTION        all|first|last|odd|even|"range"
  --position POS        bottom-right|bottom-left|top-right|top-left
  --scale FLOAT         0.1-1.0 (default: 0.25)
  --x-offset FLOAT      0.1-2.0 inches (default: 0.5)
  --y-offset FLOAT      0.1-2.0 inches (default: 0.5)
  --opacity FLOAT       0.1-1.0 (default: 1.0)
  --rotation INT        0-360 degrees (default: 0)
  --quiet               Suppress output
```

## Examples

### Example 1: Simple Contract Signing

```bash
# Sign first page of contract
python pdf_signature.py \
    --signature my_signature.png \
    --input contract.pdf \
    --pages first
```

### Example 2: Company Seal on Reports

```bash
# Add company seal to all pages
python pdf_signature.py \
    --signature company_seal.png \
    --input quarterly_reports/ \
    --output sealed_reports/ \
    --position top-right \
    --scale 0.15
```

### Example 3: Watermarked Documents

```bash
# Add semi-transparent watermark
python pdf_signature.py \
    --signature watermark.png \
    --input confidential_docs/ \
    --pages all \
    --opacity 0.3 \
    --scale 0.4
```

### Example 4: Multi-Page Signing

```bash
# Sign only specific pages
python pdf_signature.py \
    --signature initials.png \
    --input agreement.pdf \
    --pages "1,5,10,15-20" \
    --scale 0.15
```

### Example 5: Rotated Signature

```bash
# Sign with rotated signature
python pdf_signature.py \
    --signature signature.png \
    --input document.pdf \
    --rotation 15 \
    --position bottom-right
```

## Next Steps

- Try the web interface for visual feedback: `python web_interface.py`
- Experiment with different opacity levels for watermarks
- Create multiple signature PNGs for different purposes
- Automate signing with batch scripts
- Combine with PDF organization for complete workflow
