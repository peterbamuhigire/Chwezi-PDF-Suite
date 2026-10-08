#!/usr/bin/env python3
"""
Minimal Test - Verify PDF Organizer Works
Tests the basic functionality step by step
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

print("="*70)
print("  PDF Organizer - Basic Test")
print("="*70)
print()

# Test 1: Imports
print("Test 1: Checking imports...")
try:
    import anthropic  # noqa: F401  (import is the availability test)
    import openai  # noqa: F401
    import pdfplumber  # noqa: F401
    from google import genai as google_genai  # noqa: F401
    from pypdf import PdfReader  # noqa: F401
    print("✓ All imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    print("\nRun: pip install -r requirements.txt")
    input("\nPress Enter to exit...")
    sys.exit(1)

# Test 2: API Key
print("\nTest 2: Checking API key...")
print("Select provider for API test:")
print("1) Gemini")
print("2) Anthropic")
print("3) DeepSeek")
provider_choice = input("Select provider [1]: ").strip().lower()

if provider_choice in ['2', 'anthropic', 'a']:
    provider = "anthropic"
elif provider_choice in ['3', 'deepseek', 'd']:
    provider = "deepseek"
else:
    provider = "gemini"

if provider == "anthropic":
    api_key = input("Enter your Anthropic API key (or press Enter to skip): ").strip()
elif provider == "deepseek":
    api_key = input("Enter your DeepSeek API key (or press Enter to skip): ").strip()
else:
    api_key = input("Enter your Gemini API key (or press Enter to skip): ").strip()

if not api_key:
    print("⚠ Skipping API test")
else:
    print(f"✓ Using provided key: ...{api_key[-4:] if len(api_key) > 8 else '****'}")

# Test 3: Create test folders
print("\nTest 3: Creating test folders...")
test_dir = Path.home() / "pdf_organizer_test"
test_downloads = test_dir / "downloads"
test_ebooks = test_dir / "ebooks"

try:
    test_downloads.mkdir(parents=True, exist_ok=True)
    test_ebooks.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created: {test_dir}")
    print(f"  Downloads: {test_downloads}")
    print(f"  Ebooks:    {test_ebooks}")
except Exception as e:
    print(f"❌ Failed to create folders: {e}")
    input("\nPress Enter to exit...")
    sys.exit(1)

# Test 4: Test PDFOrganizer initialization
print("\nTest 4: Testing PDFOrganizer class...")
try:
    from organize_batch import BatchPDFOrganizer
    print("✓ BatchPDFOrganizer imported")
    
    # Test with valid paths but no API key
    if not api_key:
        print("⚠ Skipping initialization test (no API key)")
    else:
        try:
            organizer = BatchPDFOrganizer(
                downloads_folder=str(test_downloads),
                ebooks_folder=str(test_ebooks),
                api_key=api_key,
                provider=provider,
                dry_run=True
            )
            print("✓ PDFOrganizer initialized successfully")
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            import traceback
            print("\nTraceback:")
            print(traceback.format_exc())
    
except ImportError as e:
    print(f"❌ Cannot import BatchPDFOrganizer: {e}")
    print("\nMake sure organize_batch.py is in the same folder")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    print("\nTraceback:")
    print(traceback.format_exc())

# Test 5: Test with None values (should fail gracefully)
print("\nTest 5: Testing validation...")
try:
    from organize_batch import BatchPDFOrganizer
    
    try:
        bad_organizer = BatchPDFOrganizer(
            downloads_folder=None,
            ebooks_folder=None,
            api_key="test",
            dry_run=True
        )
        print("⚠ WARNING: None values were accepted (validation not working)")
    except ValueError as ve:
        print(f"✓ Validation working correctly: {str(ve)[:60]}...")
    except Exception as e:
        print(f"⚠ Unexpected error type: {e}")
        
except Exception as e:
    print(f"⚠ Could not test validation: {e}")

# Cleanup
print("\nTest 6: Cleanup...")
try:
    import shutil
    if test_dir.exists():
        shutil.rmtree(test_dir)
        print("✓ Cleaned up test folders")
except Exception as e:
    print(f"⚠ Cleanup warning: {e}")

# Summary
print()
print("="*70)
print("  Test Summary")
print("="*70)
print()
print("If all tests passed, the organizer should work!")
print()
print("To use it:")
print("1. Make sure you have PDFs in your Downloads folder")
print("2. Run: python organize_batch.py")
print()
print("="*70)

input("\nPress Enter to exit...")
