#!/usr/bin/env python3
"""
PDF Organizer Diagnostic Tool
Run this to check your configuration and identify issues
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

print("="*70)
print("  PDF Organizer - Diagnostic Tool")
print("="*70)
print()
api_key = None

# Check Python version
print("1. Python Version:")
print(f"   {sys.version}")
# diagnose.py must report old interpreters, so this check cannot assume the project minimum
if sys.version_info < (3, 11):  # noqa: UP036
    print("   ❌ WARNING: Python 3.11+ is required")
else:
    print("   ✓ OK")
print()

# Check imports
print("2. Checking Required Packages:")
packages = {
    'google.genai': 'google-genai',
    'anthropic': 'anthropic',
    'pdfplumber': 'pdfplumber',
    'pypdf': 'pypdf',
    'tkinter': 'tkinter (GUI)',
}

all_ok = True
for module_name, display_name in packages.items():
    try:
        __import__(module_name)
        print(f"   ✓ {display_name}")
    except ImportError:
        print(f"   ❌ {display_name} - NOT INSTALLED")
        all_ok = False

if not all_ok:
    print()
    print("   Run: pip install google-genai pdfplumber pypdf")
print()

# Check API key
print("3. API Key:")
print("   API keys are entered at runtime and are not stored or read from the environment.")
print()

# Check settings file
print("4. Settings File:")
settings_file = Path.home() / '.pdf_organizer_settings.json'
if settings_file.exists():
    print(f"   ✓ Found: {settings_file}")
    try:
        import json
        with open(settings_file) as f:
            settings = json.load(f)
        
        print()
        print("   Configured paths:")
        if settings.get('downloads_path'):
            downloads = settings['downloads_path']
            print(f"   Downloads: {downloads}")
            if Path(downloads).exists():
                print("              ✓ Exists")
            else:
                print("              ❌ Does not exist")
        else:
            print("   Downloads: Not set")
        
        if settings.get('ebooks_path'):
            ebooks = settings['ebooks_path']
            print(f"   Ebooks:    {ebooks}")
            if Path(ebooks).exists():
                print("              ✓ Exists")
            else:
                print("              ❌ Does not exist")
        else:
            print("   Ebooks:    Not set")
        
        print("   API Key:   Not stored")
    except Exception as e:
        print(f"   ⚠ Error reading settings: {e}")
else:
    print(f"   ⚠ Not found: {settings_file}")
    print("   Settings will be created on first save")
print()

# Auto-detect Downloads
print("5. Auto-Detected Paths:")
auto_downloads = Path.home() / "Downloads"
print(f"   Downloads: {auto_downloads}")
if auto_downloads.exists():
    pdf_count = len(list(auto_downloads.glob('*.pdf')))
    print(f"              ✓ Exists ({pdf_count} PDFs in root)")
else:
    print("              ❌ Does not exist")
print()

# Test PDF Organizer import
print("6. Testing PDF Organizer:")
try:
    from organize_batch import BatchPDFOrganizer
    print("   ✓ BatchPDFOrganizer class imported successfully")
    
    # Test with minimal params
    print()
    print("   Testing validation...")
    try:
        organizer = BatchPDFOrganizer(
            downloads_folder=None,
            ebooks_folder=None,
            api_key="test-key",
            dry_run=True
        )
        print("   ⚠ WARNING: Validation not working - None accepted")
    except ValueError as ve:
        print(f"   ✓ Validation working: {ve}")
    except Exception as e:
        print(f"   ⚠ Unexpected error: {e}")
    
except ImportError as e:
    print(f"   ❌ Cannot import BatchPDFOrganizer: {e}")
    print("   Make sure organize_batch.py is in the same directory")
except Exception as e:
    print(f"   ❌ Error: {e}")
print()

# Summary
print("="*70)
print("  Diagnostic Summary")
print("="*70)
print()

if all_ok and api_key:
    print("✓ All checks passed!")
    print()
    print("You should be ready to run:")
    print("  python organize_batch.py")
else:
    print("⚠ Some issues found. Please address them:")
    print()
    if not all_ok:
        print("  - Install missing packages: pip install -r requirements.txt")
    if not api_key:
        print("  - Set API key or enter it in the GUI")
    print()
    print("Then run: python organize_batch.py")

print()
print("="*70)

# Wait for user
input("Press Enter to exit...")
