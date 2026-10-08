"""
PDF Signature Tool - Core Module

Adds PNG signature images to PDFs with extensive configuration options.
No AI credits required - pure PDF manipulation.

Features:
- 4 corner positions (bottom-right, bottom-left, top-right, top-left)
- Page selection (all, first, last, odd, even, ranges)
- Skip pages (exclude specific pages from signing)
- Adjustable scaling (10-100% of A4 portrait width)
- Configurable margins (X/Y offsets in inches)
- Opacity control (10-100% transparency)
- Rotation (0-360 degrees)
- Batch processing support
"""

import json
import os
import re
from contextlib import suppress
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import ClassVar

try:
    from PIL import Image
except ImportError:
    print("ERROR: Pillow not installed. Run: pip install pillow")
    raise

try:
    import fitz
except ImportError:
    fitz = None

try:
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas
except ImportError:
    print("ERROR: ReportLab not installed. Run: pip install reportlab")
    raise

try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("ERROR: pypdf not installed. Run: pip install pypdf")
    raise


class PDFSignature:
    """Core signature placement engine"""

    VALID_POSITIONS: ClassVar[list[str]] = ['bottom-right', 'bottom-left', 'top-right', 'top-left']
    VALID_PAGE_OPTIONS: ClassVar[list[str]] = ['all', 'first', 'last', 'odd', 'even']
    A4_PORTRAIT_WIDTH_POINTS = 595.2755905511812  # 210 mm at 72 PDF points/inch

    def __init__(self, signature_image_path, position='bottom-left',
                 scale=0.3, x_offset=0.5, y_offset=0.5, opacity=1.0,
                 rotation=0, pages='all', skip_pages=''):
        """
        Initialize PDF signature configuration.

        Args:
            signature_image_path: Path to PNG signature image
            position: Corner position - 'bottom-right', 'bottom-left', 'top-right', 'top-left'
            scale: Signature width as fraction of A4 portrait width (0.1-1.0)
            x_offset: Horizontal margin from edge in inches (0.1-2.0)
            y_offset: Vertical margin from edge in inches (0.1-2.0)
            opacity: Transparency level (0.1-1.0, where 1.0 is opaque)
            rotation: Rotation angle in degrees (0-360)
            pages: Page selection - 'all', 'first', 'last', 'odd', 'even', or range
                like '1-5,10,15-20'
            skip_pages: Pages to never sign even if selected, e.g. '3' or '1,5,10-12'
        """
        # Validate signature image
        if not os.path.exists(signature_image_path):
            raise ValueError(f"Signature image not found: {signature_image_path}")

        try:
            with Image.open(signature_image_path) as img:
                if img.format != 'PNG':
                    raise ValueError("Signature must be PNG format")
                self.signature_image = img.copy()
            self.signature_path = signature_image_path
        except Exception as e:
            raise ValueError(f"Failed to load signature image: {e}") from e

        # Validate position
        if position not in self.VALID_POSITIONS:
            raise ValueError(f"Position must be one of: {self.VALID_POSITIONS}")
        self.position = position

        # Validate scale
        if not 0.1 <= scale <= 1.0:
            raise ValueError("Scale must be between 0.1 and 1.0")
        self.scale = scale

        # Validate offsets
        if not 0.1 <= x_offset <= 2.0:
            raise ValueError("X offset must be between 0.1 and 2.0 inches")
        if not 0.1 <= y_offset <= 2.0:
            raise ValueError("Y offset must be between 0.1 and 2.0 inches")
        self.x_offset = x_offset * 72  # Convert inches to points
        self.y_offset = y_offset * 72

        # Validate opacity
        if not 0.1 <= opacity <= 1.0:
            raise ValueError("Opacity must be between 0.1 and 1.0")
        self.opacity = opacity

        # Validate rotation
        if not 0 <= rotation <= 360:
            raise ValueError("Rotation must be between 0 and 360 degrees")
        self.rotation = rotation

        # Validate and parse pages
        self.pages = pages
        self._validate_pages_format()

        # Parse skip_pages into a set
        self._skip_set = (
            self._parse_page_range(skip_pages.strip())
            if skip_pages and skip_pages.strip()
            else set()
        )

    def _validate_pages_format(self):
        """Validate the pages parameter format"""
        if self.pages in self.VALID_PAGE_OPTIONS:
            return

        # Check if it's a valid range format (e.g., "1-5,10,15-20")
        if not re.match(r'^[\d\s,\-]+$', self.pages):
            raise ValueError(
                "Invalid pages format. Use 'all', 'first', 'last', 'odd', 'even', "
                "or ranges like '1-5,10,15-20'"
            )

    @staticmethod
    def _parse_page_range(range_str):
        """Parse a range string like '1,3,5-10' into a set of page numbers."""
        pages = set()
        for part in range_str.split(','):
            part = part.strip()
            if not part:
                continue
            if '-' in part:
                start, end = part.split('-', 1)
                pages.update(range(int(start), int(end) + 1))
            else:
                pages.add(int(part))
        return pages

    def _should_sign_page(self, page_num, total_pages):
        """
        Determine if a page should be signed based on pages filter and skip_pages.

        Args:
            page_num: Current page number (1-indexed)
            total_pages: Total number of pages in PDF

        Returns:
            bool: True if page should be signed
        """
        # Skip pages are never signed regardless of other settings
        if page_num in self._skip_set:
            return False


        if self.pages == 'all':
            return True
        elif self.pages == 'first':
            return page_num == 1
        elif self.pages == 'last':
            return page_num == total_pages
        elif self.pages == 'odd':
            return page_num % 2 == 1
        elif self.pages == 'even':
            return page_num % 2 == 0
        else:
            return page_num in self._parse_page_range(self.pages)

    def _calculate_position(self, page_width, page_height, sig_width, sig_height):
        """
        Calculate x,y coordinates based on position and offsets.

        Args:
            page_width: Page width in points
            page_height: Page height in points
            sig_width: Signature width in points
            sig_height: Signature height in points

        Returns:
            tuple: (x, y) coordinates in points
        """
        # PDF coordinates: (0,0) at bottom-left
        if self.position == 'bottom-right':
            x = page_width - sig_width - self.x_offset
            y = self.y_offset
        elif self.position == 'bottom-left':
            x = self.x_offset
            y = self.y_offset
        elif self.position == 'top-right':
            x = page_width - sig_width - self.x_offset
            y = page_height - sig_height - self.y_offset
        elif self.position == 'top-left':
            x = self.x_offset
            y = page_height - sig_height - self.y_offset

        return x, y

    def _calculate_signature_size(self, image_ratio):
        """
        Calculate signature dimensions using a fixed A4 portrait reference.

        The scale setting is intentionally independent of the actual PDF page
        size and orientation, so 10% is always 10% of an A4 portrait sheet's
        width.
        """
        sig_width = self.A4_PORTRAIT_WIDTH_POINTS * self.scale
        sig_height = sig_width * image_ratio
        return sig_width, sig_height

    def _create_signature_overlay(self, page_width, page_height,
                                   mediabox_left=0, mediabox_bottom=0,
                                   page_rotation=0):
        """
        Create ReportLab canvas with positioned, rotated, transparent signature.

        Args:
            page_width: Visible page width in points (mediabox right - left)
            page_height: Visible page height in points (mediabox top - bottom)
            mediabox_left: Left offset of mediabox from PDF origin (default 0)
            mediabox_bottom: Bottom offset of mediabox from PDF origin (default 0)
            page_rotation: Page rotation in degrees clockwise (0, 90, 180, 270)

        Returns:
            BytesIO: PDF overlay as bytes

        Note on page_rotation:
            PDF /Rotate specifies clockwise rotation applied by the viewer.
            We apply the inverse transform so that the user's chosen position
            (bottom-left, top-right, etc.) always matches the visual corner.

            Transforms (visual → physical) per rotation:
              90°  CW: translate(W, 0),  rotate(90)  → (W-vis_y, vis_x)
              180°:    translate(W, H),  rotate(180) → (W-vis_x, H-vis_y)
              270° CW: translate(0, H),  rotate(270) → (vis_y,   H-vis_x)
        """
        packet = BytesIO()

        # Canvas must cover the full PDF coordinate space so the overlay
        # merges correctly even when the mediabox has a non-zero origin.
        canvas_width = mediabox_left + page_width
        canvas_height = mediabox_bottom + page_height

        # Visual dimensions depend on rotation (90/270 swap width and height)
        if page_rotation in (90, 270):
            vis_width = page_height
            vis_height = page_width
        else:
            vis_width = page_width
            vis_height = page_height

        c = canvas.Canvas(packet, pagesize=(canvas_width, canvas_height))

        # Shift origin to the mediabox lower-left corner
        if mediabox_left != 0 or mediabox_bottom != 0:
            c.translate(mediabox_left, mediabox_bottom)

        # Apply inverse-rotation transform so all drawing uses visual coords
        if page_rotation == 90:
            c.translate(page_width, 0)
            c.rotate(90)
        elif page_rotation == 180:
            c.translate(page_width, page_height)
            c.rotate(180)
        elif page_rotation == 270:
            c.translate(0, page_height)
            c.rotate(270)

        # Calculate signature dimensions using fixed A4 portrait width.
        sig_width, sig_height = self._calculate_signature_size(
            self.signature_image.height / self.signature_image.width
        )

        # Warn if signature is too large
        if sig_width > vis_width * 0.5 or sig_height > vis_height * 0.5:
            print(f"Warning: Signature is large ({sig_width:.0f}x{sig_height:.0f} pts "
                  f"on {vis_width:.0f}x{vis_height:.0f} page)")

        # Calculate position using visual dimensions
        x, y = self._calculate_position(vis_width, vis_height, sig_width, sig_height)

        # Apply opacity
        c.setFillAlpha(self.opacity)

        # Handle user-requested signature rotation
        if self.rotation != 0:
            c.saveState()
            center_x = x + sig_width / 2
            center_y = y + sig_height / 2
            c.translate(center_x, center_y)
            c.rotate(self.rotation)
            c.translate(-sig_width / 2, -sig_height / 2)
            c.drawImage(ImageReader(self.signature_image),
                       0, 0,
                       width=sig_width,
                       height=sig_height,
                       mask='auto')
            c.restoreState()
        else:
            c.drawImage(ImageReader(self.signature_image),
                       x, y,
                       width=sig_width,
                       height=sig_height,
                       mask='auto')

        c.save()
        packet.seek(0)
        return packet

    @staticmethod
    def _match_overlay_boxes(overlay_page, target_page):
        """
        Force the overlay page boxes to match the target page exactly.

        Some PDFs use non-default media/crop boxes. If the stamp page keeps
        ReportLab's default boxes, pypdf can merge the content onto a page
        with mismatched boundaries, which may shift layout in some viewers.
        """
        for box_name in ('mediabox', 'cropbox', 'trimbox', 'bleedbox', 'artbox'):
            target_box = getattr(target_page, box_name, None)
            if target_box is not None:
                setattr(overlay_page, box_name, target_box)

    def _get_processed_signature_bytes(self):
        """
        Build the final PNG that will be stamped onto each page.

        Opacity and user rotation are applied directly to the image so the PDF
        page content can remain untouched and the signature behaves like a
        visual overlay instead of inline page content.
        """
        image = self.signature_image.convert("RGBA").copy()

        if self.opacity < 1.0:
            alpha = image.getchannel("A")
            alpha = alpha.point(lambda px: int(px * self.opacity))
            image.putalpha(alpha)

        if self.rotation:
            # PIL rotates counter-clockwise; PDF UI convention is clockwise.
            image = image.rotate(-self.rotation, expand=True, resample=Image.Resampling.BICUBIC)

        output = BytesIO()
        image.save(output, format="PNG")
        return output.getvalue(), image.width, image.height

    def _add_signature_to_pdf_with_pymupdf(self, input_pdf_path, output_pdf_path):
        """Stamp the signature as an overlay using PyMuPDF + ReportLab.

        Uses show_pdf_page (never insert_image) so every page is stamped
        reliably regardless of rotation or internal page structure.
        Placement matches the same fixed A4 portrait-width sizing rule used
        by the pypdf overlay path, so the configured corner, scale, and
        offsets remain exact regardless of page size or rotation.
        """
        doc = fitz.open(input_pdf_path)
        try:
            total_pages = doc.page_count
            pages_signed = 0

            for page_index in range(total_pages):
                page_num = page_index + 1
                if not self._should_sign_page(page_num, total_pages):
                    continue

                page = doc.load_page(page_index)

                # Build overlay in mediabox coordinates with an inverse-rotation
                # transform baked in. show_pdf_page places the overlay into
                # the mediabox; the viewer then applies the page's /Rotate to
                # the merged content. Pre-applying the inverse rotation keeps
                # the signature visually upright in the user's chosen corner
                # regardless of page orientation (portrait vs landscape) or
                # /Rotate value.
                mb = page.mediabox
                mb_width = float(mb.width)
                mb_height = float(mb.height)
                try:
                    page_rotation = int(page.rotation) % 360
                except (AttributeError, TypeError):
                    page_rotation = 0

                # show_pdf_page maps the overlay's full pagesize onto the
                # target mediabox rect, so build the canvas at mediabox
                # dimensions with a 0-origin (no mediabox offset baked in).
                overlay_pdf = self._create_signature_overlay(
                    mb_width, mb_height,
                    0, 0,
                    page_rotation,
                )

                overlay_doc = fitz.open("pdf", overlay_pdf.read())
                page.show_pdf_page(mb, overlay_doc, 0, overlay=True)
                overlay_doc.close()
                pages_signed += 1

            os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)
            doc.save(output_pdf_path)
            return total_pages, pages_signed
        finally:
            doc.close()

    def add_signature_to_pdf(self, input_pdf_path, output_pdf_path=None):
        """
        Sign a single PDF with page filtering.

        Args:
            input_pdf_path: Path to input PDF
            output_pdf_path: Path for output PDF (defaults to input_signed.pdf)

        Returns:
            dict: Processing result with success status and details
        """
        result = {
            'input_path': input_pdf_path,
            'output_path': output_pdf_path,
            'success': False,
            'total_pages': 0,
            'pages_signed': 0,
            'error': None
        }

        try:
            # Validate input
            if not os.path.exists(input_pdf_path):
                raise ValueError(f"Input PDF not found: {input_pdf_path}")

            # Determine output path
            if output_pdf_path is None:
                input_path = Path(input_pdf_path)
                output_pdf_path = str(input_path.parent / f"{input_path.stem}_signed.pdf")

            result['output_path'] = output_pdf_path

            if os.path.abspath(output_pdf_path) == os.path.abspath(input_pdf_path):
                raise ValueError(
                    "Output path is the same as the input path; "
                    "refusing to overwrite the source PDF"
                )

            if fitz is not None:
                total_pages, pages_signed = self._add_signature_to_pdf_with_pymupdf(
                    input_pdf_path, output_pdf_path
                )
                result['total_pages'] = total_pages
                result['pages_signed'] = pages_signed
                result['success'] = True
                return result

            # Read input PDF
            reader = PdfReader(input_pdf_path)
            writer = PdfWriter()

            total_pages = len(reader.pages)
            result['total_pages'] = total_pages
            pages_signed = 0

            # Process each page
            for page_num, page in enumerate(reader.pages, start=1):
                # Check if this page should be signed
                if self._should_sign_page(page_num, total_pages):
                    # Get page dimensions and position from mediabox
                    mediabox = page.mediabox
                    mediabox_left = float(mediabox.left)
                    mediabox_bottom = float(mediabox.bottom)
                    page_width = float(mediabox.right) - mediabox_left
                    page_height = float(mediabox.top) - mediabox_bottom

                    # Read page rotation so positions match what the user sees
                    try:
                        page_rotation = int(page.rotation) % 360
                    except (AttributeError, TypeError):
                        page_rotation = 0

                    # Create signature overlay
                    overlay_pdf = self._create_signature_overlay(
                        page_width, page_height,
                        mediabox_left, mediabox_bottom,
                        page_rotation
                    )
                    overlay_reader = PdfReader(overlay_pdf)
                    overlay_page = overlay_reader.pages[0]
                    self._match_overlay_boxes(overlay_page, page)

                    # Merge as a true overlay without allowing page expansion.
                    page.merge_page(overlay_page, expand=False, over=True)
                    pages_signed += 1

                # Add page to output (signed or unsigned)
                writer.add_page(page)

            # Write output PDF
            os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)
            with open(output_pdf_path, 'wb') as output_file:
                writer.write(output_file)

            result['pages_signed'] = pages_signed
            result['success'] = True

        except Exception as e:
            result['error'] = str(e)

        return result

    def batch_sign_pdfs(self, pdf_directory, output_directory=None):
        """
        Sign all PDFs in a directory.

        Args:
            pdf_directory: Directory containing PDFs to sign
            output_directory: Output directory (defaults to pdf_directory/signed/)

        Returns:
            dict: Batch processing results
        """
        # Validate input directory
        if not os.path.isdir(pdf_directory):
            raise ValueError(f"Input directory not found: {pdf_directory}")

        # Determine output directory
        if output_directory is None:
            output_directory = os.path.join(pdf_directory, 'signed')

        os.makedirs(output_directory, exist_ok=True)

        # Find all PDFs
        pdf_files = []
        output_resolved = Path(output_directory).resolve()
        for root, dirs, files in os.walk(pdf_directory):
            # Do not descend into the output directory (would re-sign signed PDFs)
            dirs[:] = [d for d in dirs if Path(root, d).resolve() != output_resolved]
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))

        # Process each PDF
        results = {
            'total_pdfs': len(pdf_files),
            'successful': 0,
            'failed': 0,
            'files': [],
            'log_path': None
        }

        for pdf_path in pdf_files:
            # Determine output path (maintain relative structure)
            rel_path = os.path.relpath(pdf_path, pdf_directory)
            output_path = os.path.join(output_directory, rel_path)

            # Process PDF
            result = self.add_signature_to_pdf(pdf_path, output_path)

            # Track results
            if result['success']:
                results['successful'] += 1
            else:
                results['failed'] += 1

            results['files'].append(result)

        # Write log file
        log_path = os.path.join(output_directory, 'signature_log.json')
        self._write_log(results['files'], log_path)
        results['log_path'] = log_path

        return results

    def _write_log(self, file_results, log_path):
        """Write processing log to JSON file"""
        log_data = {
            'signed_files': []
        }

        # Load existing log if it exists
        if os.path.exists(log_path):
            try:
                with open(log_path, encoding='utf-8') as f:
                    log_data = json.load(f)
            except (OSError, ValueError):
                # Keep the unreadable log for inspection and start fresh
                stamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
                backup = f"{os.path.splitext(log_path)[0]}.corrupt-{stamp}.json"
                with suppress(OSError):
                    os.replace(log_path, backup)
                log_data = {'signed_files': []}
        if not isinstance(log_data, dict):
            log_data = {'signed_files': []}
        log_data.setdefault('signed_files', [])

        # Add new entries
        for result in file_results:
            if result['success']:
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'input_path': result['input_path'],
                    'output_path': result['output_path'],
                    'signature': self.signature_path,
                    'pages_filter': self.pages,
                    'position': self.position,
                    'scale': self.scale,
                    'x_offset': self.x_offset / 72,  # Convert back to inches
                    'y_offset': self.y_offset / 72,
                    'opacity': self.opacity,
                    'rotation': self.rotation,
                    'total_pages': result['total_pages'],
                    'pages_signed': result['pages_signed'],
                    'success': True
                }
                log_data['signed_files'].append(log_entry)

        # Write log
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(log_data, f, indent=2)


def _legacy_main():
    """Launch the tkinter GUI for signing PDFs."""
    import sys
    import threading
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    from ui_theme import BODY_FONT

    missing = check_dependencies()
    if missing:
        print(f"ERROR: Missing dependencies: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        sys.exit(1)

    class SignatureGUI:
        POSITIONS: ClassVar[list[tuple[str, str, int, int]]] = [
            ('↖', 'top-left',     0, 0),
            ('↗', 'top-right',    0, 1),
            ('↙', 'bottom-left',  1, 0),
            ('↘', 'bottom-right', 1, 1),
        ]

        def __init__(self, root):
            self.root = root
            self.root.title('PDF Signature Tool')
            self.root.resizable(False, False)

            self.sig_path   = tk.StringVar()
            self.input_path = tk.StringVar()
            self.output_path = tk.StringVar()
            self.batch_mode  = tk.BooleanVar(value=False)
            self.pages_var   = tk.StringVar(value='all')
            self.range_var   = tk.StringVar(value='1')
            self.skip_var  = tk.StringVar(value='')
            self.position    = tk.StringVar(value='bottom-left')
            self.scale       = tk.DoubleVar(value=25)
            self.x_offset    = tk.DoubleVar(value=0.5)
            self.y_offset    = tk.DoubleVar(value=0.5)
            self.opacity     = tk.DoubleVar(value=100)
            self.rotation    = tk.IntVar(value=0)

            self._pos_buttons = {}
            self._build()
            self._update_preview()

        # ── layout ──────────────────────────────────────────────

        def _build(self):
            pad = {'padx': 8, 'pady': 4}

            # ── Files ────────────────────────────────────────────
            f_files = ttk.LabelFrame(self.root, text=' Files ', padding=6)
            f_files.grid(row=0, column=0, columnspan=2, sticky='ew', **pad)

            self._file_row(f_files, 0, 'Signature PNG:', self.sig_path,
                           self._browse_sig)
            self._file_row(f_files, 1, 'Input PDF / folder:', self.input_path,
                           self._browse_input)
            self._file_row(f_files, 2, 'Output:', self.output_path,
                           self._browse_output)
            ttk.Checkbutton(f_files, text='Batch mode (sign all PDFs in folder)',
                            variable=self.batch_mode,
                            command=self._on_batch_toggle
                            ).grid(row=3, column=0, columnspan=3, sticky='w', pady=2)

            # ── Config ───────────────────────────────────────────
            f_cfg = ttk.LabelFrame(self.root, text=' Configuration ', padding=6)
            f_cfg.grid(row=1, column=0, sticky='nsew', **pad)

            # pages
            ttk.Label(f_cfg, text='Pages:').grid(row=0, column=0, sticky='w')
            pages_cb = ttk.Combobox(f_cfg, textvariable=self.pages_var, width=10,
                                    state='readonly',
                                    values=['all','first','last','odd','even','range'])
            pages_cb.grid(row=0, column=1, sticky='w', padx=4)
            pages_cb.bind('<<ComboboxSelected>>', self._on_pages_change)
            self._range_label = ttk.Label(f_cfg, text='Range:')
            self._range_entry = ttk.Entry(f_cfg, textvariable=self.range_var, width=12)

            ttk.Label(f_cfg, text='Exempt pages:').grid(
                row=2, column=0, sticky='w', pady=2)
            ttk.Entry(f_cfg, textvariable=self.skip_var, width=16).grid(
                row=2, column=1, sticky='w', padx=4)
            ttk.Label(f_cfg, text='e.g. 3  or  1,5,9-12',
                      foreground='#888').grid(row=2, column=2, sticky='w')

            # position grid
            ttk.Label(f_cfg, text='Position:').grid(row=3, column=0, sticky='w', pady=(8,2))
            pos_frame = ttk.Frame(f_cfg)
            pos_frame.grid(row=3, column=1, sticky='w', padx=4)
            for (arrow, pos, r, c) in self.POSITIONS:
                btn = tk.Button(pos_frame, text=f'{arrow}\n{pos}',
                                width=9, height=2, relief='raised',
                                command=lambda p=pos: self._select_pos(p))
                btn.grid(row=r, column=c, padx=2, pady=2)
                self._pos_buttons[pos] = btn
            self._select_pos('bottom-left')

            # sliders
            sliders = [
                ('Size (% of A4 width):',   self.scale,    10, 100, 1),
                ('H margin (inches):',       self.x_offset, 0.1, 2.0, 0.1),
                ('V margin (inches):',       self.y_offset, 0.1, 2.0, 0.1),
                ('Opacity (%):',             self.opacity,  10, 100, 1),
                ('Rotation (°):',            self.rotation, 0,  360, 1),
            ]
            for i, (label, var, lo, hi, res) in enumerate(sliders, start=5):
                ttk.Label(f_cfg, text=label).grid(row=i, column=0, sticky='w', pady=2)
                val_lbl = ttk.Label(f_cfg, width=5, anchor='e')
                val_lbl.grid(row=i, column=2, padx=(0,4))
                sl = ttk.Scale(f_cfg, from_=lo, to=hi, variable=var,
                               orient='horizontal', length=160,
                               command=lambda v, lbl=val_lbl, res=res:
                                   self._on_slider(v, lbl, res))
                sl.grid(row=i, column=1, padx=4)
                self._on_slider(var.get(), val_lbl, res)

            # ── Preview ──────────────────────────────────────────
            f_prev = ttk.LabelFrame(self.root, text=' Preview ', padding=6)
            f_prev.grid(row=1, column=1, sticky='nsew', **pad)

            self._canvas = tk.Canvas(f_prev, width=220, height=280,
                                     bg='#e8e8e8', highlightthickness=1,
                                     highlightbackground='#999')
            self._canvas.pack()

            # Trace all config vars → redraw preview
            for var in (self.position, self.scale, self.x_offset,
                        self.y_offset, self.opacity, self.rotation,
                        self.pages_var):
                var.trace_add('write', lambda *_: self._update_preview())

            # ── Sign button + log ─────────────────────────────────
            ttk.Button(self.root, text='✍  Sign PDF(s)',
                       command=self._sign).grid(
                row=2, column=0, columnspan=2, pady=6, ipadx=20, ipady=6)

            self._log = tk.Text(self.root, height=6, width=70,
                                state='disabled', font=('Consolas', 9))
            self._log.grid(row=3, column=0, columnspan=2,
                           padx=8, pady=(0, 8), sticky='ew')

        def _file_row(self, parent, row, label, var, cmd):
            ttk.Label(parent, text=label).grid(row=row, column=0, sticky='w', pady=2)
            ttk.Entry(parent, textvariable=var, width=38).grid(
                row=row, column=1, padx=4)
            ttk.Button(parent, text='Browse', command=cmd).grid(
                row=row, column=2)

        # ── event handlers ───────────────────────────────────────

        def _browse_sig(self):
            p = filedialog.askopenfilename(title='Select signature PNG',
                                           filetypes=[('PNG image', '*.png')])
            if p:
                self.sig_path.set(p)

        def _browse_input(self):
            if self.batch_mode.get():
                p = filedialog.askdirectory(title='Select folder of PDFs')
            else:
                p = filedialog.askopenfilename(title='Select PDF',
                                               filetypes=[('PDF', '*.pdf')])
            if p:
                self.input_path.set(p)
                self._auto_output(p)

        def _browse_output(self):
            if self.batch_mode.get():
                p = filedialog.askdirectory(title='Select output folder')
            else:
                p = filedialog.asksaveasfilename(
                    title='Save signed PDF as',
                    defaultextension='.pdf',
                    filetypes=[('PDF', '*.pdf')])
            if p:
                self.output_path.set(p)

        def _auto_output(self, inp):
            from pathlib import Path as _Path
            if self.batch_mode.get():
                self.output_path.set(str(_Path(inp) / 'signed'))
            else:
                p = _Path(inp)
                self.output_path.set(str(p.parent / f'{p.stem}_signed.pdf'))

        def _on_batch_toggle(self):
            inp = self.input_path.get()
            if inp:
                self._auto_output(inp)

        def _on_pages_change(self, _=None):
            if self.pages_var.get() == 'range':
                self._range_label.grid(row=1, column=0, sticky='w')
                self._range_entry.grid(row=1, column=1, sticky='w', padx=4)
            else:
                self._range_label.grid_remove()
                self._range_entry.grid_remove()

        def _select_pos(self, pos):
            self.position.set(pos)
            for p, btn in self._pos_buttons.items():
                btn.config(relief='sunken' if p == pos else 'raised',
                           bg='#4a90d9' if p == pos else 'SystemButtonFace',
                           fg='white' if p == pos else 'black')

        def _on_slider(self, val, label, res):
            v = float(val)
            label.config(text=f'{v:.1f}' if res < 1 else str(round(v)))
            self._update_preview()

        # ── preview canvas ───────────────────────────────────────

        def _update_preview(self):
            if not hasattr(self, '_canvas'):
                return
            c = self._canvas
            c.delete('all')

            cw, ch = 220, 280
            margin = 14

            # A4 portrait reference page
            ph = ch - 2 * margin
            pw = ph * (210 / 297)
            px = (cw - pw) / 2
            py = margin
            c.create_rectangle(px, py, px + pw, py + ph,
                                fill='white', outline='#444', width=2)

            scale     = self.scale.get() / 100
            x_off_px  = self.x_offset.get() * 20
            y_off_px  = self.y_offset.get() * 20
            sig_w     = pw * scale
            sig_h     = sig_w * 0.4       # preview aspect ratio
            alpha     = self.opacity.get() / 100
            rot       = self.rotation.get()
            pos       = self.position.get()

            # Position in page-local coords (top-left origin for canvas)
            if pos == 'bottom-left':
                sx = px + x_off_px
                sy = py + ph - y_off_px - sig_h
            elif pos == 'bottom-right':
                sx = px + pw - x_off_px - sig_w
                sy = py + ph - y_off_px - sig_h
            elif pos == 'top-left':
                sx = px + x_off_px
                sy = py + y_off_px
            else:  # top-right
                sx = px + pw - x_off_px - sig_w
                sy = py + y_off_px

            # Draw a blue rectangle for the signature (with simple opacity via stipple)
            fill = '#4a90d9'
            stipple = '' if alpha > 0.7 else ('gray50' if alpha > 0.4 else 'gray25')
            cx2 = sx + sig_w
            cy2 = sy + sig_h

            if rot != 0:
                import math
                cx = sx + sig_w / 2
                cy = sy + sig_h / 2
                corners = [(sx, sy), (cx2, sy), (cx2, cy2), (sx, cy2)]
                rad = math.radians(rot)
                cos_r, sin_r = math.cos(rad), math.sin(rad)
                pts = []
                for (x, y) in corners:
                    dx, dy = x - cx, y - cy
                    pts += [cx + dx * cos_r - dy * sin_r,
                            cy + dx * sin_r + dy * cos_r]
                c.create_polygon(pts, fill=fill, outline='#2060a0',
                                 width=1, stipple=stipple)
            else:
                c.create_rectangle(sx, sy, cx2, cy2,
                                   fill=fill, outline='#2060a0',
                                   width=1, stipple=stipple)

            c.create_text(cw // 2, ch // 2 + 8,
                          text='Preview', fill='#bbb', font=(BODY_FONT, 9))

        # ── signing ──────────────────────────────────────────────

        def _log_write(self, msg):
            self._log.config(state='normal')
            self._log.insert('end', msg + '\n')
            self._log.see('end')
            self._log.config(state='disabled')

        def _sign(self):
            sig   = self.sig_path.get().strip()
            inp   = self.input_path.get().strip()
            out   = self.output_path.get().strip()
            pages = (self.range_var.get().strip()
                     if self.pages_var.get() == 'range'
                     else self.pages_var.get())

            if not sig:
                messagebox.showerror('Missing', 'Please select a signature PNG.')
                return
            if not inp:
                messagebox.showerror('Missing', 'Please select an input PDF or folder.')
                return
            if not out:
                messagebox.showerror('Missing', 'Please set an output path.')
                return

            def run():
                try:
                    signer = PDFSignature(
                        signature_image_path=sig,
                        position=self.position.get(),
                        scale=self.scale.get() / 100,
                        x_offset=self.x_offset.get(),
                        y_offset=self.y_offset.get(),
                        opacity=self.opacity.get() / 100,
                        rotation=self.rotation.get(),
                        pages=pages,
                        skip_pages=self.skip_var.get().strip(),
                    )
                    if self.batch_mode.get():
                        self._log_write(f'Batch signing: {inp} → {out}')
                        res = signer.batch_sign_pdfs(inp, out)
                        self._log_write(
                            f'Done — {res["successful"]} signed, '
                            f'{res["failed"]} failed  |  log: {res["log_path"]}')
                    else:
                        self._log_write(f'Signing: {inp}')
                        res = signer.add_signature_to_pdf(inp, out)
                        if res['success']:
                            self._log_write(
                                f'Done — {res["pages_signed"]}/{res["total_pages"]} '
                                f'pages signed  |  output: {res["output_path"]}')
                        else:
                            self._log_write(f'ERROR: {res["error"]}')
                except Exception as e:
                    self._log_write(f'ERROR: {e}')

            threading.Thread(target=run, daemon=True).start()

    root = tk.Tk()
    SignatureGUI(root)
    root.mainloop()


def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []

    try:
        import PIL  # noqa: F401  (availability probe: the import is the test)
    except ImportError:
        missing.append('pillow')

    try:
        import reportlab  # noqa: F401  (availability probe)
    except ImportError:
        missing.append('reportlab')

    try:
        import pypdf  # noqa: F401  (availability probe)
    except ImportError:
        missing.append('pypdf')

    return missing


def main():
    """Launch the maintained themed signing interface."""
    import sys

    missing = check_dependencies()
    if missing:
        print(f"ERROR: Missing dependencies: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        sys.exit(1)

    from signature_gui import launch_signature_gui

    launch_signature_gui(PDFSignature)


if __name__ == '__main__':
    main()
