"""
Interactive PDF Signature Setup

Step-by-step wizard for signing PDFs with PNG signatures.
No AI credits required - pure PDF manipulation.
"""

import os
import sys
from pathlib import Path

# Fix Windows console encoding issues
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Check dependencies first
print("=" * 60)
print("PDF SIGNATURE SETUP - Dependency Check")
print("=" * 60)

try:
    from pdf_signature import PDFSignature, check_dependencies
except ImportError:
    print("\nERROR: pdf_signature.py not found!")
    print("Make sure you're running this from the correct directory.")
    sys.exit(1)

missing = check_dependencies()
if missing:
    print(f"\nMissing dependencies: {', '.join(missing)}")
    print("\nInstall them explicitly, then run this command again:")
    print(f"  {sys.executable} -m pip install {' '.join(missing)}")
    sys.exit(1)

print("OK All dependencies installed")
print()


def print_header(step, title):
    """Print formatted step header"""
    print()
    print("=" * 60)
    print(f"STEP {step}: {title}")
    print("=" * 60)


def get_file_path(prompt, extension=None, must_exist=True):
    """Get and validate a file path from user"""
    while True:
        path = input(f"{prompt}: ").strip().strip('"')

        if not path:
            print("  Error: Path cannot be empty")
            continue

        if must_exist and not os.path.exists(path):
            print(f"  Error: File not found: {path}")
            continue

        if extension and not path.lower().endswith(extension):
            print(f"  Error: File must be {extension} format")
            continue

        return path


def get_directory_path(prompt, must_exist=True):
    """Get and validate a directory path from user"""
    while True:
        path = input(f"{prompt}: ").strip().strip('"')

        if not path:
            print("  Error: Path cannot be empty")
            continue

        if must_exist and not os.path.isdir(path):
            print(f"  Error: Directory not found: {path}")
            continue

        return path


def get_choice(prompt, options):
    """Get a choice from a numbered menu"""
    print(f"\n{prompt}")
    for i, option in enumerate(options, start=1):
        print(f"  {i}. {option}")

    while True:
        try:
            choice = input("\nEnter number: ").strip()
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
            else:
                print(f"  Error: Enter a number between 1 and {len(options)}")
        except ValueError:
            print("  Error: Enter a valid number")


def get_float(prompt, min_val, max_val, default=None):
    """Get a float value within a range"""
    default_text = f" (default: {default})" if default is not None else ""
    while True:
        value = input(f"{prompt} [{min_val}-{max_val}]{default_text}: ").strip()

        if not value and default is not None:
            return default

        try:
            val = float(value)
            if min_val <= val <= max_val:
                return val
            else:
                print(f"  Error: Value must be between {min_val} and {max_val}")
        except ValueError:
            print("  Error: Enter a valid number")


def get_int(prompt, min_val, max_val, default=None):
    """Get an integer value within a range"""
    default_text = f" (default: {default})" if default is not None else ""
    while True:
        value = input(f"{prompt} [{min_val}-{max_val}]{default_text}: ").strip()

        if not value and default is not None:
            return default

        try:
            val = int(value)
            if min_val <= val <= max_val:
                return val
            else:
                print(f"  Error: Value must be between {min_val} and {max_val}")
        except ValueError:
            print("  Error: Enter a valid integer")


def main():
    """Main interactive setup"""
    print()
    print("=" * 60)
    print("PDF SIGNATURE TOOL - Interactive Setup")
    print("=" * 60)
    print()
    print("This wizard will guide you through signing PDFs with your")
    print("signature image. No AI credits required!")
    print()

    # Step 1: Select signature image
    print_header(1, "Select Signature Image")
    print("Choose a PNG image to use as your signature.")
    print()
    signature_path = get_file_path("Path to signature PNG", extension=".png")
    print(f"OK Using signature: {signature_path}")

    # Step 2: Select PDFs
    print_header(2, "Select PDFs to Sign")
    print("Choose single PDF file or directory of PDFs.")
    print()
    input_type = get_choice(
        "What would you like to sign?", ["Single PDF file", "All PDFs in a directory"]
    )

    if input_type == "Single PDF file":
        input_path = get_file_path("Path to PDF file", extension=".pdf")
        batch_mode = False
    else:
        input_path = get_directory_path("Path to directory containing PDFs")
        batch_mode = True

    print(f"OK Input: {input_path}")

    # Step 3: Configure output
    print_header(3, "Configure Output Location")
    if batch_mode:
        print("Signed PDFs will be saved to a subdirectory.")
        print()
        use_default = input("Use default output directory? (Y/n): ").strip().lower()
        if use_default in ["", "y", "yes"]:
            output_path = os.path.join(input_path, "signed")
        else:
            output_path = get_directory_path("Output directory", must_exist=False)
    else:
        print("Where should the signed PDF be saved?")
        print()
        use_default = input("Save next to original with '_signed' suffix? (Y/n): ").strip().lower()
        if use_default in ["", "y", "yes"]:
            input_file = Path(input_path)
            output_path = str(input_file.parent / f"{input_file.stem}_signed.pdf")
        else:
            output_path = get_file_path("Output PDF path", extension=".pdf", must_exist=False)

    print(f"OK Output: {output_path}")

    # Step 4: Page selection
    print_header(4, "Choose Pages to Sign")
    print("Which pages should receive the signature?")
    print()
    page_option = get_choice(
        "Page selection:",
        [
            "All pages",
            "First page only",
            "Last page only",
            "Odd pages only",
            "Even pages only",
            "Custom range (e.g., 1-5,10,15-20)",
        ],
    )

    if page_option == "All pages":
        pages = "all"
    elif page_option == "First page only":
        pages = "first"
    elif page_option == "Last page only":
        pages = "last"
    elif page_option == "Odd pages only":
        pages = "odd"
    elif page_option == "Even pages only":
        pages = "even"
    else:
        pages = input("Enter page range (e.g., 1-5,10,15-20): ").strip()

    print(f"OK Pages: {pages}")

    # Step 5: Choose position
    print_header(5, "Choose Signature Position")
    print("Where should the signature appear on the page?")
    print()
    print("  ┌─────────────────┐")
    print("  │ 3           4   │")
    print("  │                 │")
    print("  │                 │")
    print("  │ 1           2   │")
    print("  └─────────────────┘")
    print()
    position_map = {1: "bottom-left", 2: "bottom-right", 3: "top-left", 4: "top-right"}

    while True:
        try:
            pos_num = int(input("Enter position number (1-4): ").strip())
            if pos_num in position_map:
                position = position_map[pos_num]
                break
            else:
                print("  Error: Enter 1, 2, 3, or 4")
        except ValueError:
            print("  Error: Enter a valid number")

    print(f"OK Position: {position}")

    # Step 6: Configure size
    print_header(6, "Configure Signature Size")
    print("How large should the signature be?")
    print("Size is specified as percentage of A4 portrait width (10-100%).")
    print()
    scale_percent = get_float("Signature size (%)", 10, 100, default=25)
    scale = scale_percent / 100.0
    print(f"OK Scale: {scale_percent}% of A4 portrait width")

    # Step 7: Configure margins
    print_header(7, "Configure Margins")
    print("Set the distance from page edges (in inches).")
    print()
    x_offset = get_float("Horizontal margin (inches)", 0.1, 2.0, default=0.5)
    y_offset = get_float("Vertical margin (inches)", 0.1, 2.0, default=0.5)
    print(f'OK Margins: {x_offset}" horizontal, {y_offset}" vertical')

    # Step 8: Configure opacity
    print_header(8, "Configure Opacity")
    print("Set signature transparency (10-100%).")
    print("100% = fully opaque, 10% = very transparent")
    print()
    opacity_percent = get_float("Opacity (%)", 10, 100, default=100)
    opacity = opacity_percent / 100.0
    print(f"OK Opacity: {opacity_percent}%")

    # Step 9: Configure rotation
    print_header(9, "Configure Rotation")
    print("Rotate the signature (0-360 degrees).")
    print("0° = no rotation, 90° = rotated right, etc.")
    print()
    rotation = get_int("Rotation (degrees)", 0, 360, default=0)
    print(f"OK Rotation: {rotation}°")

    # Step 10: Configure skip pages (optional)
    print_header(10, "Skip Pages (Optional)")
    print("Enter pages to exclude from signing (applied after page selection).")
    print("Examples: '2,5' or '1-3,10' or leave empty to skip none")
    print()
    skip_pages = input("Skip pages (press Enter to skip none): ").strip()
    if skip_pages:
        print(f"OK Skip pages: {skip_pages}")
    else:
        print("OK No pages skipped")

    # Configuration summary
    print()
    print("=" * 60)
    print("CONFIGURATION SUMMARY")
    print("=" * 60)
    print(f"Signature:  {signature_path}")
    print(f"Input:      {input_path}")
    print(f"Output:     {output_path}")
    print(f"Pages:      {pages}")
    if skip_pages:
        print(f"Skip pages: {skip_pages}")
    print(f"Position:   {position}")
    print(f"Size:       {scale_percent}% of A4 portrait width")
    print(f'Margins:    {x_offset}" H, {y_offset}" V')
    print(f"Opacity:    {opacity_percent}%")
    print(f"Rotation:   {rotation}°")
    print("=" * 60)
    print()

    # Confirmation
    confirm = input("Proceed with signing? (Y/n): ").strip().lower()
    if confirm not in ["", "y", "yes"]:
        print("\nAborted.")
        return

    # Processing
    print()
    print("=" * 60)
    print("PROCESSING")
    print("=" * 60)
    print()

    try:
        # Create signature instance
        signer = PDFSignature(
            signature_image_path=signature_path,
            position=position,
            scale=scale,
            x_offset=x_offset,
            y_offset=y_offset,
            opacity=opacity,
            rotation=rotation,
            pages=pages,
            skip_pages=skip_pages,
        )

        if batch_mode:
            # Batch processing
            print(f"Signing all PDFs in: {input_path}")
            print(f"Output directory: {output_path}")
            print()

            results = signer.batch_sign_pdfs(input_path, output_path)

            print()
            print("=" * 60)
            print("RESULTS")
            print("=" * 60)
            print(f"Total PDFs:  {results['total_pdfs']}")
            print(f"Successful:  {results['successful']}")
            print(f"Failed:      {results['failed']}")
            print(f"Log file:    {results['log_path']}")
            print()

            if results["failed"] > 0:
                print("Failed files:")
                for file_result in results["files"]:
                    if not file_result["success"]:
                        print(f"  - {file_result['input_path']}: {file_result['error']}")

        else:
            # Single file processing
            print(f"Signing: {input_path}")
            print()

            result = signer.add_signature_to_pdf(input_path, output_path)

            print()
            print("=" * 60)
            print("RESULT")
            print("=" * 60)

            if result["success"]:
                print("OK Success!")
                print(f"  Total pages:  {result['total_pages']}")
                print(f"  Pages signed: {result['pages_signed']}")
                print(f"  Output file:  {result['output_path']}")
            else:
                print(f"FAIL Failed: {result['error']}")

        print()

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback

        traceback.print_exc()
        return

    # Exit prompt
    print()
    input("Press Enter to exit...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAborted by user.")
        sys.exit(1)
