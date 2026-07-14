# ADR 0005: Integrate OCRmyPDF as the first scanned-PDF adapter

Status: proposed  
Date: 2026-07-14  
Owner: extraction maintainer

## Context

OCR must preserve born-digital PDFs, support page-aware modes and expose image-processing warnings. Building a custom raster/Tesseract pipeline would duplicate mature work.

## Options

1. Invoke Tesseract directly and reconstruct PDFs.
2. Integrate OCRmyPDF for PDF workflows, with a smaller image-OCR adapter where needed.
3. Use a remote OCR provider.

## Decision

Propose option 2. OCRmyPDF is optional and local. Automatic mode first detects usable text; force mode requires explicit selection. Remote OCR is outside the initial release.

## Consequences

- OCR extra requires Python 3.11+ and platform-specific system/language dependencies.
- Temporary-space estimation and worker isolation are required.
- PDF/A claims depend on validation, not successful process exit alone.
- Page-level warnings and backend versions appear in results.

## Verification

The corpus includes born-digital, image-only, mixed, rotated, multilingual and encrypted PDFs. Tests prove automatic mode does not rasterise usable born-digital pages unnecessarily.

