#!/usr/bin/env python3
"""
PDF Organizer - Watch Mode
Monitors Downloads folder and auto-organizes PDFs as they arrive
"""

import sys
import threading
import time
import types
from datetime import datetime
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

class PDFWatcher(FileSystemEventHandler):
    """Watches for new PDF files and organizes them"""

    def __init__(self, downloads_folder, ebooks_folder, api_key, provider, batch_delay=10,
                 content_analysis=False):
        """
        Initialize the PDF watcher

        Args:
            downloads_folder: Folder to watch for new PDFs
            ebooks_folder: Destination folder for organized PDFs
            api_key: API key for the selected provider
            provider: AI provider (gemini, anthropic, deepseek)
            batch_delay: Seconds to wait before processing (allows multiple PDFs to arrive)
        """
        self.downloads_folder = Path(downloads_folder)
        self.ebooks_folder = Path(ebooks_folder)
        self.api_key = api_key
        self.provider = provider
        self.batch_delay = max(1, batch_delay)
        self.content_analysis = content_analysis

        # Track pending PDFs
        self.pending_pdfs = set()
        self.process_timer = None
        self.lock = threading.Lock()
        # Serialises batches so two timers never move files or write the log concurrently
        self.processing_lock = threading.Lock()

        # Statistics
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'start_time': datetime.now()
        }

        print(f"\n👀 Watching: {self.downloads_folder}")
        print(f"📁 Organizing to: {self.ebooks_folder}")
        print(f"🤖 Using: {provider.title()}")
        print(f"⏱️  Batch delay: {batch_delay} seconds")
        print(f"\n{'='*70}")
        print("  WATCH MODE ACTIVE - Press Ctrl+C to stop")
        print(f"{'='*70}\n")

    def on_created(self, event):
        """Called when a file is created"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process PDF files
        if file_path.suffix.lower() != '.pdf':
            return

        # Ignore temporary files
        if file_path.name.startswith('.') or file_path.name.startswith('~'):
            return

        # Ignore our own moves when the library sits inside the watched folder
        if file_path.resolve().is_relative_to(self.ebooks_folder.resolve()):
            return

        print(f"\n🔔 New PDF detected: {file_path.name}")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        with self.lock:
            self.pending_pdfs.add(file_path)
            self._schedule_processing()

            print(f"   ⏳ Waiting {self.batch_delay}s for more PDFs...")

    def on_moved(self, event):
        """Called when a file is renamed (e.g. browser .crdownload -> .pdf)"""
        if event.is_directory:
            return

        dest_path = getattr(event, 'dest_path', '')
        if not dest_path or Path(dest_path).suffix.lower() != '.pdf':
            return

        self.on_created(types.SimpleNamespace(src_path=dest_path, is_directory=False))

    def _schedule_processing(self):
        """(Re)start the batch timer. Caller must hold self.lock."""
        if self.process_timer:
            self.process_timer.cancel()

        self.process_timer = threading.Timer(
            self.batch_delay,
            self._process_pending_pdfs
        )
        self.process_timer.start()

    def _process_pending_pdfs(self):
        """Process all pending PDFs in a batch, one batch at a time"""
        with self.processing_lock:
            self._process_batch()

    def _process_batch(self):
        with self.lock:
            if not self.pending_pdfs:
                return

            # Get list of PDFs to process
            pdfs_to_process = list(self.pending_pdfs)
            self.pending_pdfs.clear()

        print(f"\n{'='*70}")
        print(f"  🚀 Processing {len(pdfs_to_process)} PDF(s)")
        print(f"{'='*70}\n")

        # Wait a bit more to ensure files are fully written
        time.sleep(2)

        # Filter out files that don't exist or are still being written
        valid_pdfs = []
        for pdf_path in pdfs_to_process:
            if not pdf_path.exists():
                print(f"⚠️  Skipping {pdf_path.name} - file no longer exists")
                continue

            # Check if file is still being written (size changes)
            try:
                size1 = pdf_path.stat().st_size
                time.sleep(0.5)
                size2 = pdf_path.stat().st_size

                if size1 != size2:
                    print(f"⚠️  Skipping {pdf_path.name} - still being written")
                    # Add back to pending
                    with self.lock:
                        self.pending_pdfs.add(pdf_path)
                        self._schedule_processing()
                    continue

                valid_pdfs.append(pdf_path)
            except Exception as e:
                print(f"⚠️  Error checking {pdf_path.name}: {e}")
                continue

        if not valid_pdfs:
            print("ℹ️  No valid PDFs to process\n")  # noqa: RUF001 - intentional info glyph in console output
            return

        # Create a temporary downloads folder with just these PDFs
        # Or process them directly
        try:
            from organize_batch import BatchPDFOrganizer

            # Content previews leave the machine only when the user opted in
            with BatchPDFOrganizer(
                downloads_folder=self.downloads_folder,
                ebooks_folder=self.ebooks_folder,
                api_key=self.api_key,
                provider=self.provider,
                dry_run=False,
                use_content_analysis=self.content_analysis
            ) as organizer:
                # Get PDF info
                pdf_list = []
                for pdf_path in valid_pdfs:
                    info = organizer.get_pdf_info(pdf_path)
                    pdf_list.append(info)

                # Load categories
                categories = organizer.load_or_analyze_categories()

                # Batch categorize
                categorizations = organizer.batch_categorize_all(pdf_list, categories)

                if not categorizations:
                    print("❌ Categorization failed")
                    self.stats['failed'] += len(valid_pdfs)
                    return

                # Match and move
                moved = 0
                categorization_map = {cat['number']: cat for cat in categorizations}

                for i, pdf_info in enumerate(pdf_list, 1):
                    cat_result = categorization_map.get(i, {
                        'category': 'Uncategorized',
                        'confidence': 'low',
                        'rename': None
                    })

                    result = {
                        'source': pdf_info['path'],
                        'filename': pdf_info['filename'],
                        'category': cat_result.get('category', 'Uncategorized'),
                        'confidence': cat_result.get('confidence', 'low'),
                        'rename_to': cat_result.get('rename')
                    }

                    print(f"\n📄 {pdf_info['filename']}")
                    print(f"   → Category: {result['category']}")
                    print(f"   → Confidence: {result['confidence']}")

                    # Move the file; one bad file must not abort the batch
                    try:
                        destination = organizer.move_pdf(result)
                    except Exception as move_error:
                        print(f"❌ Failed to move {pdf_info['filename']}: {move_error}")
                        self.stats['failed'] += 1
                        self.stats['total_processed'] += 1
                        continue

                    organizer.log['organized_files'].append(
                        {**result, 'destination': str(destination)}
                    )
                    moved += 1
                    self.stats['successful'] += 1
                    self.stats['total_processed'] += 1

                # Update log
                if moved:
                    organizer.save_log()

                print(f"\n✅ Organized {moved} of {len(pdf_list)} PDF(s)")
                self._print_stats()

        except Exception as e:
            print(f"\n❌ Error processing PDFs: {e}")
            import traceback
            print(traceback.format_exc())
            self.stats['failed'] += len(valid_pdfs)

        print(f"\n{'='*70}")
        print("  👀 Continuing to watch for new PDFs...")
        print(f"{'='*70}\n")

    def _print_stats(self):
        """Print current statistics"""
        runtime = datetime.now() - self.stats['start_time']
        hours = int(runtime.total_seconds() // 3600)
        minutes = int((runtime.total_seconds() % 3600) // 60)

        print("\n📊 Statistics:")
        print(f"   Total processed: {self.stats['total_processed']}")
        print(f"   Successful: {self.stats['successful']}")
        print(f"   Failed: {self.stats['failed']}")
        print(f"   Runtime: {hours}h {minutes}m")


def main():
    """Main watch mode function"""
    import argparse

    parser = argparse.ArgumentParser(
        description='PDF Organizer - Watch Mode',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Watch Downloads folder with Gemini
  python watch_organizer.py --ebooks F:/ebooks --provider gemini --api-key YOUR_KEY

  # Watch with custom batch delay
  python watch_organizer.py --ebooks F:/ebooks --provider deepseek --api-key YOUR_KEY --delay 30
        """
    )

    default_downloads = str(Path.home() / "Downloads")

    parser.add_argument('--downloads', default=default_downloads,
                       help=f'Downloads folder to watch (default: {default_downloads})')
    parser.add_argument('--ebooks', required=True,
                       help='Ebooks folder for organized PDFs (e.g., F:/ebooks)')
    parser.add_argument('--provider', choices=['gemini', 'anthropic', 'deepseek'],
                       required=True, help='AI provider to use')
    parser.add_argument('--api-key', required=True,
                       help='API key for the selected provider')
    parser.add_argument('--delay', type=int, default=10,
                       help='Batch delay in seconds (default: 10)')
    parser.add_argument('--content-analysis', action='store_true',
                       help='Send text previews of unclear files to the AI provider '
                            '(off by default)')

    args = parser.parse_args()

    # Validate folders
    downloads_folder = Path(args.downloads)
    ebooks_folder = Path(args.ebooks)

    if not downloads_folder.exists():
        print(f"❌ Error: Downloads folder not found: {downloads_folder}")
        sys.exit(1)

    if not ebooks_folder.exists():
        create = input(
            f"\n📁 Ebooks folder doesn't exist. Create {ebooks_folder}? (Y/n): "
        ).strip().lower()
        if create in ['', 'y', 'yes']:
            ebooks_folder.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created: {ebooks_folder}")
        else:
            print("❌ Ebooks folder is required")
            sys.exit(1)

    # Create event handler
    event_handler = PDFWatcher(
        downloads_folder=downloads_folder,
        ebooks_folder=ebooks_folder,
        api_key=args.api_key,
        provider=args.provider,
        batch_delay=args.delay,
        content_analysis=args.content_analysis
    )

    # Create observer
    observer = Observer()
    observer.schedule(event_handler, str(downloads_folder), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n\n{'='*70}")
        print("  🛑 Stopping watch mode...")
        print(f"{'='*70}\n")
        observer.stop()
        event_handler._print_stats()
        print("\n👋 Watch mode stopped. Goodbye!\n")

    observer.join()


if __name__ == "__main__":
    main()
