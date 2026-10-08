#!/usr/bin/env python3
"""
Setup script for PDF Organizer
Helps with initial configuration and testing
"""

import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def check_python_version():
    """Check if Python version is adequate"""
    print_header("Checking Python Version")
    version = sys.version_info
    print(f"Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print("✅ Python version OK")
    return True

def install_dependencies():
    """Install required packages"""
    print_header("Installing Dependencies")
    
    try:
        print("Installing packages from requirements.txt...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        print("Try running manually: pip install -r requirements.txt")
        return False

def test_imports():
    """Test if all required modules can be imported"""
    print_header("Testing Package Imports")
    
    packages = [
        ('google.genai', 'google-genai'),
        ('anthropic', 'anthropic'),
        ('pdfplumber', 'pdfplumber'),
        ('pypdf', 'pypdf'),
        ('tkinter', 'tkinter (GUI)')
    ]
    
    all_ok = True
    for module_name, display_name in packages:
        try:
            __import__(module_name)
            print(f"✅ {display_name}")
        except ImportError:
            print(f"❌ {display_name} - not found")
            all_ok = False
    
    return all_ok

def setup_api_key():
    """Explain API key requirements"""
    print_header("API Key Configuration")
    print("\nThis tool requires an API key that you enter when you start organizing.")
    print("We do not read API keys from environment variables or config files.")
    print("\nGet a key from:")
    print("- Gemini: https://aistudio.google.com/app/apikey")
    print("- Anthropic: https://console.anthropic.com/")
    return True

def configure_folders():
    """Help user configure folder paths"""
    print_header("Folder Configuration")
    
    config_file = Path.home() / '.pdf_organizer_settings.json'
    import json
    
    config = {}
    if config_file.exists():
        try:
            with open(config_file, encoding="utf-8") as f:
                config = json.load(f)
        except (OSError, ValueError) as exc:
            print(f"   Existing settings could not be read ({exc}); starting fresh.")
            config = {}
    
    # Downloads folder
    print("\n1. Downloads Folder")
    if config.get('downloads_path'):
        print(f"   Current: {config['downloads_path']}")
        change = input("   Keep this path? (y/n): ").lower()
        if change == 'y':
            downloads = config['downloads_path']
        else:
            downloads = input("   Enter Downloads folder path: ").strip()
    else:
        # Suggest default
        default_downloads = str(Path.home() / "Downloads")
        print(f"   Suggested: {default_downloads}")
        use_default = input("   Use suggested path? (y/n): ").lower()
        if use_default == 'y':
            downloads = default_downloads
        else:
            downloads = input("   Enter Downloads folder path: ").strip()
    
    # Ebooks folder
    print("\n2. Ebooks Storage Folder")
    if config.get('ebooks_path'):
        print(f"   Current: {config['ebooks_path']}")
        change = input("   Keep this path? (y/n): ").lower()
        if change == 'y':
            ebooks = config['ebooks_path']
        else:
            ebooks = input("   Enter ebooks folder path: ").strip()
    else:
        ebooks = input("   Enter ebooks folder path (e.g., F:\\ebooks): ").strip()
    
    # Verify folders exist
    if not Path(downloads).exists():
        print(f"\n⚠ Warning: {downloads} doesn't exist")
        create = input("   Create it? (y/n): ").lower()
        if create == 'y':
            Path(downloads).mkdir(parents=True, exist_ok=True)
    
    if not Path(ebooks).exists():
        print(f"\n⚠ Warning: {ebooks} doesn't exist")
        create = input("   Create it? (y/n): ").lower()
        if create == 'y':
            Path(ebooks).mkdir(parents=True, exist_ok=True)
    
    # Save config
    config['downloads_path'] = downloads
    config['ebooks_path'] = ebooks
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("\n✅ Folder paths saved")
    return True

def run_test():
    """Run a quick test"""
    print_header("Running Test")
    
    print("Testing PDF organizer import...")
    try:
        import organize_batch  # noqa: F401  (the import itself is the test)
        print("✅ PDF organizer module loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Error loading PDF organizer: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("  PDF ORGANIZER - SETUP WIZARD")
    print("="*70)
    print("\nThis wizard will help you set up the PDF Organizer tool.\n")
    
    # Step 1: Check Python
    if not check_python_version():
        sys.exit(1)
    
    # Step 2: Install dependencies
    print("\nReady to install dependencies?")
    install = input("Install now? (y/n): ").lower()
    if install == 'y':
        if not install_dependencies():
            print("\n⚠ Installation had issues. Please fix them and try again.")
            sys.exit(1)
    else:
        print("⚠ Skipping installation. Make sure to run: pip install -r requirements.txt")
    
    # Step 3: Test imports
    if not test_imports():
        print("\n⚠ Some packages are missing. Please install them.")
        sys.exit(1)
    
    # Step 4: API Key
    if not setup_api_key():
        print("\n⚠ API key setup incomplete. You can configure it later.")
    
    # Step 5: Configure folders
    configure_folders()
    
    # Step 6: Run test
    run_test()
    
    # Done!
    print_header("Setup Complete!")
    print("\nYou're all set! Here's how to use the tool:\n")
    print("GUI Version (Recommended):")
    print("  python organize_batch.py")
    print("\nCommand Line:")
    print("  python organize_batch.py --downloads <path> --ebooks <path> --api-key <key>")
    print("\nFor more information, see README.md")
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
