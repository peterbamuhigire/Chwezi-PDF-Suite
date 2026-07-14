#!/usr/bin/env python3
"""
Watch Mode Setup - Interactive configuration
"""

import importlib.util
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def main():
    print("=" * 70)
    print("  PDF Organizer - Watch Mode Setup")
    print("=" * 70)
    print()
    print("This will configure automatic PDF organization.")
    print("The watcher will run in the background and organize PDFs")
    print("as they arrive in your Downloads folder.")
    print()

    # Check packages
    print("Checking dependencies...")
    try:
        required_modules = ("google.genai", "anthropic", "openai", "pypdf", "watchdog")
        missing = [name for name in required_modules if importlib.util.find_spec(name) is None]
        if missing:
            raise ImportError(", ".join(missing))
        print("  ✓ All packages installed")
    except ImportError as e:
        print(f"  ❌ Missing package: {e}")
        print("\nRuntime installation is disabled.")
        print(f"Run explicitly: {sys.executable} -m pip install -r requirements.txt")
        input("Press Enter to exit...")
        return

    print()

    # Get Downloads folder
    auto_downloads = str(Path.home() / "Downloads")
    print(f"Downloads folder: {auto_downloads}")

    if Path(auto_downloads).exists():
        use_auto = input("Use this folder? (Y/n): ").strip().lower()
        if use_auto in ["", "y", "yes"]:
            downloads = auto_downloads
        else:
            downloads = input("Enter Downloads path: ").strip()
    else:
        downloads = input("Enter Downloads path: ").strip()

    # Get Ebooks folder
    print()
    ebooks = input("Enter Ebooks folder path (e.g., F:\\ebooks): ").strip()

    if not Path(ebooks).exists():
        create = input(f"\nCreate {ebooks}? (Y/n): ").strip().lower()
        if create in ["", "y", "yes"]:
            Path(ebooks).mkdir(parents=True, exist_ok=True)
            print("✓ Created")

    # Choose provider
    print()
    print("Choose AI Provider:")
    print("1) Gemini")
    print("2) Anthropic")
    print("3) DeepSeek")
    provider_choice = input("Select provider [1]: ").strip().lower()

    if provider_choice in ["2", "anthropic", "a"]:
        provider = "anthropic"
    elif provider_choice in ["3", "deepseek", "d"]:
        provider = "deepseek"
    else:
        provider = "gemini"

    # Get API key
    print()
    if provider == "anthropic":
        api_key = input("Enter Anthropic API key: ").strip()
    elif provider == "deepseek":
        api_key = input("Enter DeepSeek API key: ").strip()
    else:
        api_key = input("Enter Gemini API key: ").strip()

    if not api_key or api_key.strip() == "":
        print("❌ ERROR: API key is required")
        input("Press Enter to exit...")
        return

    # Batch delay
    print()
    print("Batch Delay: How long to wait for more PDFs before processing")
    print("  - Shorter delay (5-10s): Faster organization")
    print("  - Longer delay (20-30s): Better batching, lower API costs")
    delay = input("Enter delay in seconds [10]: ").strip()
    delay = int(delay) if delay else 10

    # Summary
    print()
    print("=" * 70)
    print("  Configuration Summary")
    print("=" * 70)
    print(f"Downloads: {downloads}")
    print(f"Ebooks:    {ebooks}")
    print(f"Provider:  {provider.title()}")
    print(f"API Key:   {api_key[:10]}...{api_key[-4:]}")
    print(f"Delay:     {delay} seconds")
    print()
    print("💡 Watch mode will:")
    print(f"   • Monitor {downloads} for new PDFs")
    print(f"   • Wait {delay} seconds to batch multiple PDFs together")
    print(f"   • Organize them to {ebooks}")
    print("   • Run continuously until you stop it (Ctrl+C)")
    print()

    # Confirm and start
    proceed = input("Start watch mode? (Y/n): ").strip().lower()
    if proceed not in ["", "y", "yes"]:
        print("Cancelled")
        return

    # Import and run
    print()
    print("=" * 70)
    print("  Starting Watch Mode")
    print("=" * 70)
    print()

    try:
        import time

        from watchdog.observers import Observer

        from watch_organizer import PDFWatcher

        # Create event handler
        event_handler = PDFWatcher(
            downloads_folder=downloads,
            ebooks_folder=ebooks,
            api_key=api_key,
            provider=provider,
            batch_delay=delay,
        )

        # Create observer
        observer = Observer()
        observer.schedule(event_handler, downloads, recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n\n{'=' * 70}")
            print("  🛑 Stopping watch mode...")
            print(f"{'=' * 70}\n")
            observer.stop()
            event_handler._print_stats()
            print("\n👋 Watch mode stopped. Goodbye!\n")

        observer.join()

    except Exception as e:
        print()
        print("=" * 70)
        print("  ERROR")
        print("=" * 70)
        print(f"\n{e}")

        import traceback

        print("\nFull traceback:")
        print(traceback.format_exc())

    print()
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
