#!/usr/bin/env python3
"""
PDF Content Analyzer - Enhanced text extraction for better categorization
Handles PDFs with gibberish filenames by reading actual content
"""

from pathlib import Path

from pypdf import PdfReader


class PDFContentAnalyzer:
    """Analyzes PDF content for better categorization and naming"""

    def __init__(self, max_pages=3, max_chars=2000):
        """
        Initialize content analyzer

        Args:
            max_pages: Maximum pages to extract text from (default: 3)
            max_chars: Maximum characters to extract (default: 2000)
        """
        self.max_pages = max_pages
        self.max_chars = max_chars

    def extract_text_content(self, pdf_path):
        """
        Extract text from first few pages of PDF

        Returns:
            dict with extracted text and metadata
        """
        try:
            reader = PdfReader(pdf_path)

            # Get metadata
            meta = reader.metadata
            metadata = {
                'title': meta.title if meta and meta.title else None,
                'author': meta.author if meta and meta.author else None,
                'subject': meta.subject if meta and meta.subject else None,
                'creator': meta.creator if meta and meta.creator else None,
            }

            # Extract text from first few pages
            extracted_text = []
            pages_to_read = min(self.max_pages, len(reader.pages))

            for i in range(pages_to_read):
                try:
                    page = reader.pages[i]
                    text = page.extract_text()
                    if text:
                        extracted_text.append(text)
                except Exception:  # noqa: S112  (skip pages that fail to extract)
                    continue

            # Combine and limit text
            full_text = "\n".join(extracted_text)
            if len(full_text) > self.max_chars:
                full_text = full_text[:self.max_chars] + "..."

            # Clean up text (remove excessive whitespace)
            lines = [line.strip() for line in full_text.split('\n') if line.strip()]
            clean_text = "\n".join(lines)

            return {
                'metadata': metadata,
                'text_content': clean_text,
                'has_content': bool(clean_text),
                'page_count': len(reader.pages),
                'pages_analyzed': pages_to_read
            }

        except Exception as e:
            return {
                'metadata': {},
                'text_content': '',
                'has_content': False,
                'page_count': 0,
                'pages_analyzed': 0,
                'error': str(e)
            }

    def is_gibberish_filename(self, filename):
        """
        Detect if filename looks like gibberish

        Examples of gibberish:
        - SAJSABC4345.pdf
        - 1234567890.pdf
        - aB3xY9Zq2.pdf
        - temp_file_12345.pdf
        """
        original_stem = Path(filename).stem
        stem = original_stem.lower()

        # Check various gibberish patterns
        checks = {
            'too_short': len(stem) < 5,
            'mostly_numbers': sum(c.isdigit() for c in stem) > len(stem) * 0.6,
            'all_numbers': stem.replace('_', '').replace('-', '').isdigit(),
            'random_case_mix': self._has_random_case_pattern(original_stem),
            'temp_file': stem.startswith(('temp', 'tmp', 'download', 'untitled')),
            'no_vowels': not any(c in 'aeiou' for c in stem.lower()),
        }

        # If 2 or more checks pass, consider it gibberish
        gibberish_score = sum(checks.values())

        return gibberish_score >= 2, checks

    def _has_random_case_pattern(self, text):
        """Check if text has random-looking case mixing"""
        if len(text) < 5:
            return False

        # Count case transitions (like aBcDeF)
        transitions = 0
        for i in range(len(text) - 1):
            if (
                text[i].isalpha()
                and text[i+1].isalpha()
                and text[i].islower() != text[i+1].islower()
            ):
                transitions += 1

        # If more than 3 transitions in a short string, likely random
        return transitions > 3

    def build_enhanced_prompt_data(self, pdf_path):
        """
        Build comprehensive data for AI prompt

        Returns dict with:
        - filename
        - metadata (title, author, etc.)
        - text_content (from first pages)
        - is_gibberish flag
        """
        filename = pdf_path.name
        stem = pdf_path.stem

        # Check if filename is gibberish
        is_gibberish, gibberish_checks = self.is_gibberish_filename(filename)

        # Extract content
        content_data = self.extract_text_content(pdf_path)

        # Build readable name from filename
        readable_name = stem.replace('_', ' ').replace('-', ' ')

        return {
            'filename': filename,
            'stem': stem,
            'readable_name': readable_name,
            'is_gibberish': is_gibberish,
            'gibberish_checks': gibberish_checks,
            'metadata': content_data['metadata'],
            'text_content': content_data['text_content'],
            'has_content': content_data['has_content'],
            'page_count': content_data.get('page_count', 0),
            'path': str(pdf_path)
        }


def test_analyzer():
    """Test the content analyzer"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python pdf_content_analyzer.py <pdf_file>")
        return

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"Error: File not found: {pdf_path}")
        return

    analyzer = PDFContentAnalyzer()
    data = analyzer.build_enhanced_prompt_data(pdf_path)

    print("="*70)
    print("PDF Content Analysis")
    print("="*70)
    print(f"\nFilename: {data['filename']}")
    print(f"Is Gibberish: {data['is_gibberish']}")

    if data['is_gibberish']:
        print("Gibberish Indicators:")
        for check, result in data['gibberish_checks'].items():
            if result:
                print(f"  ✓ {check}")

    print("\nMetadata:")
    for key, value in data['metadata'].items():
        if value:
            print(f"  {key}: {value}")

    print(f"\nContent Preview ({data['page_count']} total pages):")
    if data['has_content']:
        preview = data['text_content'][:500]
        print(f"{preview}...")
    else:
        print("  (No text content extracted)")

    print("\n" + "="*70)


if __name__ == "__main__":
    test_analyzer()
