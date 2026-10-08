#!/usr/bin/env python3
"""
PDF Organizer - Canonical batch organizer with CLI and GUI.

This is the single organizer implementation for the repository:
- batch AI categorization for cost-effective sorting
- optional content analysis for gibberish filenames
- CLI mode for automation
- Tkinter GUI for day-to-day use
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import threading
from collections import defaultdict
from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from queue import Empty, Queue

from anthropic import Anthropic
from google import genai
from openai import OpenAI
from pypdf import PdfReader

from pdf_content_analyzer import PDFContentAnalyzer

LogCallback = Callable[[str], None]
ProgressCallback = Callable[[int, int, str], None]

DEFAULT_CATEGORY = "Uncategorized"
CONSENT_VERSION = 2
DEFAULT_MODELS = {
    "gemini": "gemini-3.8-flash",
    "anthropic": "claude-haiku-5-5",
    "deepseek": "deepseek-flash",
}
WINDOWS_RESERVED_NAMES = frozenset(
    {"CON", "PRN", "AUX", "NUL"}
    | {f"COM{i}" for i in range(1, 10)}
    | {f"LPT{i}" for i in range(1, 10)}
)
_ILLEGAL_NAME_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_MAX_SEGMENT_LENGTH = 150


def saved_content_analysis_consent(payload) -> bool:
    """Opt-ins saved before content analysis became opt-in do not count as consent."""
    return (
        isinstance(payload, dict)
        and payload.get("consent_version") == CONSENT_VERSION
        and payload.get("use_content_analysis") is True
    )


def sanitize_path_segment(value) -> str | None:
    """Return one safe folder or file name, or None when nothing usable remains."""
    if value is None:
        return None
    cleaned = _ILLEGAL_NAME_CHARS.sub("_", str(value)).strip().rstrip(". ")
    if not cleaned or set(cleaned) <= {".", "_"}:
        return None
    if cleaned.split(".")[0].upper() in WINDOWS_RESERVED_NAMES:
        cleaned = f"_{cleaned}"
    return cleaned[:_MAX_SEGMENT_LENGTH].rstrip(". ")


def safe_category_path(category) -> Path:
    """Turn an untrusted category such as 'A/B/C' into a relative path with no traversal."""
    parts = re.split(r"[\\/]+", str(category or ""))
    segments = [segment for segment in map(sanitize_path_segment, parts) if segment]
    return Path(*segments) if segments else Path(DEFAULT_CATEGORY)


def safe_pdf_filename(name, fallback: str) -> str:
    """Turn an untrusted filename suggestion into a plain '<name>.pdf'."""
    text = "" if name is None else str(name).strip()
    if text.lower().endswith(".pdf"):
        text = text[:-4]
    stem = sanitize_path_segment(text) or sanitize_path_segment(Path(fallback).stem) or "document"
    return f"{stem}.pdf"


def normalise_categorizations(items, pdf_count: int) -> list[dict]:
    """Keep only well-formed AI categorisation items, coercing field types."""
    normalised = []
    seen = set()
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue
        number = item.get("number")
        if isinstance(number, bool) or (isinstance(number, float) and not number.is_integer()):
            continue
        try:
            number = int(number)
        except (TypeError, ValueError):
            continue
        if not 1 <= number <= pdf_count or number in seen:
            continue
        seen.add(number)
        category = item.get("category")
        rename = item.get("rename")
        normalised.append(
            {
                "number": number,
                "category": (
                    category if isinstance(category, str) and category.strip() else DEFAULT_CATEGORY
                ),
                "confidence": (
                    item.get("confidence")
                    if item.get("confidence") in {"high", "medium", "low"}
                    else "low"
                ),
                "rename": None if rename is None else str(rename),
            }
        )
    return normalised


class BatchPDFOrganizer:
    """Cost-effective organizer that categorizes PDFs in large batches."""

    DEFAULT_CHUNK_SIZE = 150

    def __init__(
        self,
        downloads_folder,
        ebooks_folder,
        api_key=None,
        dry_run=False,
        category_template=None,
        provider="gemini",
        model_name=None,
        use_content_analysis=False,
        require_api_key=True,
        logger: LogCallback | None = None,
        progress_callback: ProgressCallback | None = None,
        chunk_size=DEFAULT_CHUNK_SIZE,
    ):
        if not downloads_folder:
            raise ValueError("downloads_folder is required")
        if not ebooks_folder:
            raise ValueError("ebooks_folder is required")

        self.downloads_folder = Path(downloads_folder)
        self.ebooks_folder = Path(ebooks_folder)
        self.dry_run = dry_run
        self.api_key = (api_key or "").strip()
        self.provider = (provider or "gemini").strip().lower()
        self.use_content_analysis = use_content_analysis
        self.require_api_key = require_api_key
        self.logger = logger
        self.progress_callback = progress_callback
        self.chunk_size = max(1, int(chunk_size or self.DEFAULT_CHUNK_SIZE))

        default_template = Path(__file__).resolve().parent / "category_template.json"
        self.category_template_path = (
            Path(category_template) if category_template else default_template
        )
        self.content_analyzer = PDFContentAnalyzer() if use_content_analysis else None

        if self.provider not in DEFAULT_MODELS:
            raise ValueError(f"Unsupported provider: {provider}")
        self.model_name = model_name or DEFAULT_MODELS[self.provider]

        if self.require_api_key and not self.api_key:
            raise ValueError("API key required for the selected provider")

        self.client = None
        if self.api_key:
            if self.provider == "gemini":
                self.client = genai.Client(api_key=self.api_key)
            elif self.provider == "anthropic":
                self.client = Anthropic(api_key=self.api_key)
            else:
                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.deepseek.com",
                )

        self.log_file = self.ebooks_folder / "organization_log.json"
        self.summary = {}
        self.load_log()

    def _emit(self, message):
        if self.logger:
            self.logger(message)
        else:
            print(message)

    def _progress(self, current, total, message):
        if self.progress_callback:
            self.progress_callback(current, total, message)

    def cleanup(self):
        if hasattr(self, "client"):
            self.client = None
        if hasattr(self, "api_key"):
            self.api_key = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
        return False

    def __del__(self):
        self.cleanup()

    def load_log(self):
        self.log = {
            "organized_files": [],
            "category_map": {},
            "last_run": None,
        }
        if not self.log_file.exists():
            return
        try:
            with open(self.log_file, encoding="utf-8") as handle:
                loaded = json.load(handle)
            if not isinstance(loaded, dict):
                raise ValueError("log root is not an object")
        except (OSError, ValueError) as exc:
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = self.log_file.with_name(f"{self.log_file.stem}.corrupt-{stamp}.json")
            os.replace(self.log_file, backup)
            self._emit(f"Organization log was unreadable ({exc}); preserved it as {backup.name}")
            return
        self.log.update(loaded)
        self.log.setdefault("organized_files", [])

    def save_log(self):
        self.log["last_run"] = datetime.now().isoformat()
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        handle = tempfile.NamedTemporaryFile(  # noqa: SIM115 - delete=False temp file, closed then os.replace()d below
            "w", encoding="utf-8", dir=self.log_file.parent, suffix=".tmp", delete=False
        )
        try:
            with handle:
                json.dump(self.log, handle, indent=2, ensure_ascii=False)
            os.replace(handle.name, self.log_file)
        except BaseException:
            Path(handle.name).unlink(missing_ok=True)
            raise

    def analyze_existing_structure(self):
        self._emit("Analyzing existing ebooks folder structure...")
        categories = {}

        for root, _dirs, files in os.walk(self.ebooks_folder):
            rel_path = Path(root).relative_to(self.ebooks_folder)
            if rel_path == Path("."):
                continue

            pdf_count = len([name for name in files if name.lower().endswith(".pdf")])
            category_path = "/".join(rel_path.parts)
            categories[category_path] = {
                "count": pdf_count,
                "depth": len(rel_path.parts),
            }

        if categories:
            self._emit(f"Found {len(categories)} existing categories")
        else:
            self._emit("No existing categories found")

        return categories

    def load_category_template(self):
        template_path = self.category_template_path
        if not template_path or not Path(template_path).exists():
            return None

        try:
            with open(template_path, encoding="utf-8") as handle:
                data = json.load(handle)
        except Exception as exc:
            self._emit(f"Warning: failed to load category template {template_path}: {exc}")
            return None

        categories = {}
        for entry in data.get("categories", []):
            raw_path = entry.get("path")
            if not raw_path:
                continue
            path_str = str(raw_path).replace("\\", "/").strip("/")
            categories[path_str] = {
                "count": entry.get("count", 0),
                "depth": entry.get("depth") or len(path_str.split("/")),
            }

        self._emit(f"Using category template: {template_path} ({len(categories)} categories)")
        return categories

    def load_or_analyze_categories(self):
        template_categories = self.load_category_template()
        if template_categories:
            existing = self.analyze_existing_structure()
            for path, info in existing.items():
                if path in template_categories:
                    template_categories[path]["count"] = info.get(
                        "count",
                        template_categories[path].get("count", 0),
                    )
                else:
                    template_categories[path] = info
            return template_categories
        return self.analyze_existing_structure()

    def get_pdf_info(self, pdf_path):
        pdf_path = Path(pdf_path)

        if self.use_content_analysis and self.content_analyzer:
            data = self.content_analyzer.build_enhanced_prompt_data(pdf_path)
            return {
                "path": str(pdf_path),
                "filename": pdf_path.name,
                "stem": pdf_path.stem,
                "title": data["metadata"].get("title") or pdf_path.stem,
                "author": data["metadata"].get("author") or "",
                "is_gibberish": data["is_gibberish"],
                "text_content": data["text_content"][:1000] if data["has_content"] else "",
                "has_content": data["has_content"],
            }

        try:
            reader = PdfReader(pdf_path)
            meta = reader.metadata
            title = meta.title if meta and meta.title else pdf_path.stem
            author = meta.author if meta and meta.author else ""
        except Exception:
            title = pdf_path.stem
            author = ""

        return {
            "path": str(pdf_path),
            "filename": pdf_path.name,
            "stem": pdf_path.stem,
            "title": title,
            "author": author,
            "is_gibberish": False,
            "text_content": "",
            "has_content": False,
        }

    def build_category_text(self, categories):
        if not categories:
            return "No existing categories. Create new structure."

        lines = ["EXISTING CATEGORIES:"]
        by_depth = defaultdict(list)
        for cat, info in categories.items():
            by_depth[info["depth"]].append((cat, info["count"]))

        for depth in sorted(by_depth.keys()):
            lines.append(f"\nLevel {depth}:")
            for cat, count in sorted(by_depth[depth]):
                lines.append(f"  - {cat} ({count} PDFs)")

        return "\n".join(lines)

    def batch_categorize_all(self, pdf_list, categories):
        if not self.client:
            raise RuntimeError(
                "AI client not initialized. Provide an API key before organizing PDFs."
            )

        category_text = self.build_category_text(categories)
        pdf_descriptions = []
        for index, pdf_info in enumerate(pdf_list, 1):
            desc = f"{index}. {pdf_info['filename'][:100]}"
            if pdf_info["title"] and pdf_info["title"] != pdf_info["stem"]:
                desc += f" | Title: {str(pdf_info['title'])[:100]}"
            if pdf_info.get("is_gibberish") and pdf_info.get("has_content"):
                preview = pdf_info["text_content"][:200].replace("\n", " ")
                desc += f" | Content: {preview}..."
            pdf_descriptions.append(desc)

        prompt = f"""You are organizing {len(pdf_list)} PDFs. Categorize each one and suggest better filenames for gibberish names.

EXISTING CATEGORIES:
{category_text}

PDFs TO CATEGORIZE:
{chr(10).join(pdf_descriptions)}

IMPORTANT: Return ONLY valid JSON. No explanations, no markdown, just pure JSON.

For each PDF, provide:
- number: PDF number (1-{len(pdf_list)})
- category: matching existing category structure
- confidence: "high" or "medium" or "low"
- rename: suggested filename without .pdf extension if the current name is gibberish or unclear, otherwise null

Return a JSON array like this:
[
  {{"number": 1, "category": "Computer & ICT/Programming/Python", "confidence": "high", "rename": "Python Machine Learning Guide"}},
  {{"number": 2, "category": "Business/Finance", "confidence": "medium", "rename": null}}
]

Return ONLY the JSON array."""  # noqa: E501 - prompt text kept verbatim

        self._emit(f"Sending batch request to {self.provider.title()} for {len(pdf_list)} PDFs...")

        if self.provider == "gemini":
            message = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"temperature": 0.2, "max_output_tokens": 8000},
            )
            response_text = (message.text or "").strip()
        elif self.provider == "anthropic":
            # Current Claude models reject sampling parameters, and thinking shares max_tokens.
            # Low effort suits this high-volume classification route.
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=16000,
                output_config={"effort": "low"},
                messages=[{"role": "user", "content": prompt}],
            )
            if response.stop_reason in {"refusal", "max_tokens"}:
                self._emit(f"Claude stopped early ({response.stop_reason}).")
            response_text = "".join(
                block.text for block in (response.content or []) if hasattr(block, "text")
            ).strip()
        else:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=8000,
            )
            response_text = response.choices[0].message.content.strip()

        if "```json" in response_text:
            response_text = response_text.split("```json", 1)[1].split("```", 1)[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```", 1)[1].split("```", 1)[0].strip()

        start_idx = response_text.find("[")
        end_idx = response_text.rfind("]")
        if start_idx != -1 and end_idx != -1:
            response_text = response_text[start_idx : end_idx + 1]

        try:
            categorizations = json.loads(response_text)
        except json.JSONDecodeError:
            response_text = response_text.replace(",]", "]").replace(",}", "}").replace("'", '"')
            try:
                categorizations = json.loads(response_text)
            except json.JSONDecodeError as exc:
                self._emit(f"Could not parse AI response as JSON: {exc}")
                self._emit("Falling back to simple categorization.")
                return self.simple_fallback_categorization(pdf_list)

        if not isinstance(categorizations, list):
            self._emit(f"Expected a JSON list, got {type(categorizations).__name__}.")
            return self.simple_fallback_categorization(pdf_list)

        valid = normalise_categorizations(categorizations, len(pdf_list))
        if not valid:
            self._emit("AI response contained no usable categorizations.")
            return self.simple_fallback_categorization(pdf_list)
        if len(valid) < len(categorizations):
            self._emit(f"Ignored {len(categorizations) - len(valid)} malformed AI item(s)")
        self._emit(f"Received categorizations for {len(valid)} PDFs")
        return valid

    def simple_fallback_categorization(self, pdf_list):
        keywords = {
            "python": "Computer & ICT/Programming/Python",
            "java": "Computer & ICT/Programming/Java",
            "javascript": "Computer & ICT/Programming/JavaScript",
            "web": "Computer & ICT/Web Development",
            "business": "Business/General",
            "finance": "Business/Finance",
            "accounting": "Business/Accounting",
            "tax": "Business/Accounting/Tax",
            "science": "Science/General",
            "physics": "Science/Physics",
            "math": "Science/Mathematics",
            "biology": "Science/Biology",
        }

        results = []
        for index, pdf_info in enumerate(pdf_list, 1):
            filename_lower = pdf_info["filename"].lower()
            category = "Uncategorized"
            for keyword, mapped in keywords.items():
                if keyword in filename_lower:
                    category = mapped
                    break
            results.append(
                {
                    "number": index,
                    "category": category,
                    "confidence": "low",
                    "rename": None,
                }
            )

        self._emit(f"Categorized {len(results)} PDFs using keyword fallback")
        return results

    def find_pdfs(self):
        pdf_files = []
        for root, _dirs, files in os.walk(self.downloads_folder):
            for file_name in files:
                if file_name.lower().endswith(".pdf"):
                    pdf_files.append(Path(root) / file_name)
        return pdf_files

    def move_pdf(self, result):
        """Move one PDF into the library; category and rename are untrusted AI output."""
        source = Path(result["source"])
        library = self.ebooks_folder.resolve()
        category_path = library / safe_category_path(result.get("category"))
        filename = safe_pdf_filename(
            result.get("rename_to") or result["filename"], result["filename"]
        )

        destination = category_path / filename
        if not destination.resolve().is_relative_to(library):
            raise ValueError(f"Refusing to move outside the library: {destination}")
        category_path.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            base = destination.stem
            ext = destination.suffix
            counter = 1
            while destination.exists():
                destination = category_path / f"{base}_{counter}{ext}"
                counter += 1

        shutil.move(str(source), str(destination))
        self._emit(f"Moved: {source.name} -> {destination}")
        return destination

    def organize_pdfs(self):
        self._emit(f"Scanning {self.downloads_folder} for PDFs...")
        pdf_files = self.find_pdfs()
        total_files = len(pdf_files)
        if not pdf_files:
            self.summary = {"total_files": 0, "processed": 0, "moved": 0, "dry_run": self.dry_run}
            self._emit("No PDFs found")
            return []

        self._emit(f"Found {total_files} PDFs")
        categories = self.load_or_analyze_categories()

        pdf_list = []
        self._emit("Reading PDF metadata and optional content previews...")
        for index, pdf_path in enumerate(pdf_files, 1):
            self._progress(index, total_files, f"Reading {pdf_path.name}")
            pdf_list.append(self.get_pdf_info(pdf_path))
        self._emit(f"Prepared metadata for {len(pdf_list)} PDFs")

        all_categorizations = []
        chunk_total = (len(pdf_list) + self.chunk_size - 1) // self.chunk_size

        for start in range(0, len(pdf_list), self.chunk_size):
            chunk = pdf_list[start : start + self.chunk_size]
            chunk_index = (start // self.chunk_size) + 1
            self._emit(f"Processing chunk {chunk_index}/{chunk_total} ({len(chunk)} PDFs)...")
            categorizations = self.batch_categorize_all(chunk, categories)
            for item in categorizations:
                item["number"] += start
            all_categorizations.extend(categorizations)

        if not all_categorizations:
            self.summary = {
                "total_files": total_files,
                "processed": 0,
                "moved": 0,
                "dry_run": self.dry_run,
            }
            self._emit("Categorization failed")
            return []

        categorization_map = {item["number"]: item for item in all_categorizations}
        results = []
        for index, pdf_info in enumerate(pdf_list, 1):
            cat_result = categorization_map.get(
                index,
                {"category": "Uncategorized", "confidence": "low", "rename": None},
            )
            results.append(
                {
                    "source": pdf_info["path"],
                    "filename": pdf_info["filename"],
                    "category": cat_result.get("category", "Uncategorized"),
                    "confidence": cat_result.get("confidence", "low"),
                    "rename_to": cat_result.get("rename"),
                }
            )

        category_counts = defaultdict(int)
        for result in results:
            category_counts[result["category"]] += 1

        self._emit("=" * 70)
        self._emit("CATEGORIZATION SUMMARY")
        self._emit("=" * 70)
        for category, count in sorted(category_counts.items()):
            self._emit(f"{category}: {count} file(s)")

        moved_count = 0
        failed = []
        if self.dry_run:
            self._emit("Dry run enabled. No files were moved.")
        else:
            self._emit("Moving files...")
            try:
                for index, result in enumerate(results, 1):
                    self._progress(index, len(results), f"Moving {Path(result['source']).name}")
                    try:
                        destination = self.move_pdf(result)
                    except Exception as exc:
                        failed.append({**result, "error": str(exc)})
                        self._emit(f"Failed to move {Path(result['source']).name}: {exc}")
                        continue
                    self.log["organized_files"].append({**result, "destination": str(destination)})
                    moved_count += 1
            finally:
                if moved_count:
                    self.save_log()
            self._emit(f"Organized {moved_count} PDFs")
            if failed:
                self._emit(f"{len(failed)} PDF(s) could not be moved and were left in place")

        self.summary = {
            "total_files": total_files,
            "processed": len(results),
            "moved": moved_count,
            "failed": failed,
            "dry_run": self.dry_run,
            "categories": dict(category_counts),
        }
        return results


def launch_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext, ttk

    from ui_theme import apply_ttk_theme, load_theme, save_theme, style_text_widget

    settings_file = Path.home() / ".pdf_organizer_settings.json"

    class OrganizerGUI:
        def __init__(self, root):
            self.root = root
            self.root.title("PDF Organizer")
            self.root.geometry("960x760")
            self.root.minsize(840, 640)

            self.downloads_path = tk.StringVar(value=str(Path.home() / "Downloads"))
            self.ebooks_path = tk.StringVar()
            self.api_key = tk.StringVar()
            self.provider = tk.StringVar(value="deepseek")
            self.category_template = tk.StringVar()
            self.dry_run = tk.BooleanVar(value=True)
            self.use_content_analysis = tk.BooleanVar(value=False)
            self.status_text = tk.StringVar(value="Idle")
            self.progress_value = tk.DoubleVar(value=0.0)
            self.log_queue = Queue()
            self.worker = None
            self.theme_mode = load_theme()

            self._load_settings()
            self.palette = apply_ttk_theme(self.root, self.theme_mode)
            self._build()
            self.root.after(100, self._drain_queue)

        def _build(self):
            outer_pad = {"padx": 22, "pady": 10}
            card_pad = {"padx": 0, "pady": 8}

            main = ttk.Frame(self.root, padding=(22, 18), style="App.TFrame")
            main.grid(row=0, column=0, sticky="nsew")
            self.root.columnconfigure(0, weight=1)
            self.root.rowconfigure(0, weight=1)
            main.columnconfigure(0, weight=1)
            main.rowconfigure(5, weight=1)

            hero = ttk.Frame(main, padding=(18, 16), style="Card.TFrame")
            hero.grid(row=0, column=0, sticky="ew", **card_pad)
            hero.columnconfigure(0, weight=1)
            ttk.Label(hero, text="PDF Organizer", style="Title.TLabel").grid(
                row=0, column=0, sticky="w"
            )
            ttk.Label(
                hero,
                text=(
                    "Sort a folder of PDFs in batches. Start with a dry run to inspect the "
                    "proposed categories before any file is moved."
                ),
                style="Muted.TLabel",
                wraplength=650,
            ).grid(row=1, column=0, sticky="w", pady=(5, 0))
            self.status_badge = ttk.Label(
                hero, textvariable=self.status_text, style="Status.TLabel"
            )
            self.status_badge.grid(row=0, column=1, rowspan=2, sticky="e", padx=(18, 0))

            files = ttk.LabelFrame(
                main, text="Folders and category template", padding=14, style="Card.TLabelframe"
            )
            files.grid(row=1, column=0, sticky="ew", **card_pad)
            files.columnconfigure(1, weight=1)

            self._file_row(
                files, 0, "Downloads folder:", self.downloads_path, self._browse_downloads
            )
            self._file_row(files, 1, "Ebooks folder:", self.ebooks_path, self._browse_ebooks)
            self._file_row(
                files, 2, "Category template:", self.category_template, self._browse_template
            )

            options = ttk.LabelFrame(
                main, text="Categorization settings", padding=14, style="Card.TLabelframe"
            )
            options.grid(row=2, column=0, sticky="ew", **card_pad)
            options.columnconfigure(1, weight=1)

            ttk.Label(options, text="Provider:").grid(row=0, column=0, sticky="w")
            provider_box = ttk.Combobox(
                options,
                textvariable=self.provider,
                state="readonly",
                values=("deepseek", "gemini", "anthropic"),
                width=18,
            )
            provider_box.grid(row=0, column=1, sticky="w", padx=4, pady=2)

            ttk.Label(options, text="API key:").grid(row=1, column=0, sticky="w")
            self.api_entry = ttk.Entry(options, textvariable=self.api_key, show="*", width=52)
            self.api_entry.grid(row=1, column=1, sticky="ew", padx=4, pady=2)
            ttk.Button(options, text="Show/Hide", command=self._toggle_api_key).grid(
                row=1, column=2, padx=4
            )

            ttk.Checkbutton(
                options,
                text="Dry run (preview only, do not move files)",
                variable=self.dry_run,
                command=self._sync_run_button,
            ).grid(row=2, column=0, columnspan=3, sticky="w", pady=2)
            ttk.Checkbutton(
                options,
                text="Send text previews of unclear files to the AI provider (better renaming)",
                variable=self.use_content_analysis,
            ).grid(row=3, column=0, columnspan=3, sticky="w", pady=2)

            actions = ttk.Frame(main, style="App.TFrame")
            actions.grid(row=3, column=0, sticky="ew", pady=(12, 6))
            self.run_button = ttk.Button(
                actions, text="Start dry run", command=self._run, style="Primary.TButton"
            )
            self.run_button.pack(side="left")
            ttk.Button(actions, text="Save settings", command=self._save_settings).pack(
                side="left", padx=(8, 0)
            )
            ttk.Button(actions, text="View organization log", command=self._view_log).pack(
                side="left", padx=(8, 0)
            )
            self.theme_button = ttk.Button(actions, command=self._toggle_theme)
            self.theme_button.pack(side="right")
            self._sync_run_button()
            self._sync_theme_button()

            progress_frame = ttk.Frame(main, style="App.TFrame")
            progress_frame.grid(row=4, column=0, sticky="ew", **outer_pad)
            progress_frame.columnconfigure(0, weight=1)
            ttk.Label(progress_frame, text="Progress", style="Subtitle.TLabel").grid(
                row=0, column=0, sticky="w"
            )
            self.progress = ttk.Progressbar(
                progress_frame, maximum=100, variable=self.progress_value
            )
            self.progress.grid(row=1, column=0, sticky="ew", pady=(5, 0))

            log_frame = ttk.LabelFrame(main, text="Activity", padding=14, style="Card.TLabelframe")
            log_frame.grid(row=5, column=0, sticky="nsew", **card_pad)
            log_frame.columnconfigure(0, weight=1)
            log_frame.rowconfigure(0, weight=1)
            self.log_text = scrolledtext.ScrolledText(
                log_frame, height=18, font=("Cascadia Mono", 9)
            )
            self.log_text.grid(row=0, column=0, sticky="nsew")
            style_text_widget(self.log_text, self.palette)

        def _file_row(self, parent, row, label, variable, command):
            ttk.Label(parent, text=label, style="Card.TLabel").grid(
                row=row, column=0, sticky="w", pady=4
            )
            ttk.Entry(parent, textvariable=variable).grid(
                row=row, column=1, sticky="ew", padx=10, pady=4
            )
            ttk.Button(parent, text="Browse", command=command).grid(row=row, column=2, pady=4)

        def _browse_downloads(self):
            folder = filedialog.askdirectory(title="Select Downloads Folder")
            if folder:
                self.downloads_path.set(folder)

        def _browse_ebooks(self):
            folder = filedialog.askdirectory(title="Select Ebooks Folder")
            if folder:
                self.ebooks_path.set(folder)

        def _browse_template(self):
            path = filedialog.askopenfilename(
                title="Select Category Template",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )
            if path:
                self.category_template.set(path)

        def _toggle_api_key(self):
            show = self.api_entry.cget("show")
            self.api_entry.configure(show="" if show == "*" else "*")

        def _save_settings(self, notify=True):
            payload = {
                "downloads_path": self.downloads_path.get(),
                "ebooks_path": self.ebooks_path.get(),
                "provider": self.provider.get(),
                "api_key": self.api_key.get().strip(),
                "category_template": self.category_template.get(),
                "use_content_analysis": self.use_content_analysis.get(),
                "consent_version": CONSENT_VERSION,
                "dry_run": self.dry_run.get(),
            }
            try:
                with open(settings_file, "w", encoding="utf-8") as handle:
                    json.dump(payload, handle, indent=2)
            except OSError:
                messagebox.showwarning(
                    "Settings not saved",
                    "Could not save organizer settings. Your API key will not be remembered.",
                )
                return
            if notify:
                messagebox.showinfo("Saved", "Organizer settings saved.")

        def _load_settings(self):
            if not settings_file.exists():
                return
            try:
                with open(settings_file, encoding="utf-8") as handle:
                    payload = json.load(handle)
                self.downloads_path.set(payload.get("downloads_path", self.downloads_path.get()))
                self.ebooks_path.set(payload.get("ebooks_path", ""))
                self.provider.set(payload.get("provider", self.provider.get()))
                self.api_key.set(payload.get("api_key", ""))
                self.category_template.set(payload.get("category_template", ""))
                self.use_content_analysis.set(saved_content_analysis_consent(payload))
                self.dry_run.set(payload.get("dry_run", True))
            except (OSError, ValueError, AttributeError, tk.TclError) as exc:
                self.log_queue.put(
                    ("log", f"Saved settings could not be loaded ({exc}); using defaults.")
                )

        def _view_log(self):
            log_file = Path(self.ebooks_path.get().strip()) / "organization_log.json"
            if not log_file.exists():
                messagebox.showinfo("No Log", "No organization log found yet.")
                return

            window = tk.Toplevel(self.root)
            window.title("Organization Log")
            window.geometry("700x480")
            apply_ttk_theme(window, self.theme_mode)
            text = scrolledtext.ScrolledText(window, font=("Consolas", 9))
            text.pack(fill="both", expand=True, padx=8, pady=8)
            style_text_widget(text, self.palette)
            with open(log_file, encoding="utf-8") as handle:
                text.insert("1.0", json.dumps(json.load(handle), indent=2, ensure_ascii=False))
            text.configure(state="disabled")

        def _append_log(self, message):
            self.log_text.insert("end", message + "\n")
            self.log_text.see("end")

        def _set_status(self, value):
            self.status_text.set(value)

        def _sync_run_button(self):
            self.run_button.configure(
                text="Preview organization" if self.dry_run.get() else "Organize PDFs"
            )

        def _sync_theme_button(self):
            next_theme = "light" if self.theme_mode == "dark" else "dark"
            self.theme_button.configure(text=f"Use {next_theme} theme")

        def _toggle_theme(self):
            self.theme_mode = "light" if self.theme_mode == "dark" else "dark"
            self.palette = apply_ttk_theme(self.root, self.theme_mode)
            style_text_widget(self.log_text, self.palette)
            save_theme(self.theme_mode)
            self._sync_theme_button()

        def _set_progress(self, current, total, message):
            percent = 0 if total <= 0 else (current / total) * 100
            self.progress_value.set(percent)
            self.status_text.set(message)

        def _run(self):
            downloads = self.downloads_path.get().strip()
            ebooks = self.ebooks_path.get().strip()
            api_key = self.api_key.get().strip()

            if not downloads:
                messagebox.showerror("Missing", "Please select the Downloads folder.")
                return
            if not Path(downloads).is_dir():
                messagebox.showerror(
                    "Folder not found", "The selected Downloads folder does not exist."
                )
                return
            if not ebooks:
                messagebox.showerror("Missing", "Please select the Ebooks folder.")
                return
            if not api_key:
                messagebox.showerror("Missing", "Please enter an API key.")
                return

            Path(ebooks).mkdir(parents=True, exist_ok=True)
            self._save_settings(notify=False)

            self.log_text.delete("1.0", "end")
            self.progress_value.set(0)
            self._set_status("Starting...")
            self.run_button.configure(state="disabled")

            self.worker = threading.Thread(
                target=self._run_worker,
                args=(downloads, ebooks, api_key),
                daemon=True,
            )
            self.worker.start()

        def _run_worker(self, downloads, ebooks, api_key):
            def log_callback(message):
                self.log_queue.put(("log", message))

            def progress_callback(current, total, message):
                self.log_queue.put(("progress", (current, total, message)))

            try:
                with BatchPDFOrganizer(
                    downloads_folder=downloads,
                    ebooks_folder=ebooks,
                    api_key=api_key,
                    provider=self.provider.get(),
                    dry_run=self.dry_run.get(),
                    category_template=self.category_template.get().strip() or None,
                    use_content_analysis=self.use_content_analysis.get(),
                    logger=log_callback,
                    progress_callback=progress_callback,
                ) as organizer:
                    results = organizer.organize_pdfs()
                    summary = organizer.summary

                if summary.get("dry_run"):
                    log_callback(f"Dry run complete. Reviewed {summary.get('processed', 0)} PDFs.")
                else:
                    log_callback(f"Complete. Organized {summary.get('moved', 0)} PDFs.")
                failed = summary.get("failed", [])
                self.log_queue.put(
                    ("status", f"Done with {len(failed)} failure(s)" if failed else "Done")
                )
                self.log_queue.put(("done", results))
            except Exception as exc:
                self.log_queue.put(("log", f"ERROR: {exc}"))
                self.log_queue.put(("status", "Failed"))

        def _drain_queue(self):
            try:
                while True:
                    kind, payload = self.log_queue.get_nowait()
                    if kind == "log":
                        self._append_log(payload)
                    elif kind == "progress":
                        self._set_progress(*payload)
                    elif kind == "status":
                        self._set_status(payload)
                        if payload in {"Done", "Failed"}:
                            self.run_button.configure(state="normal")
                    elif kind == "done":
                        self.progress_value.set(100)
            except Empty:
                pass
            finally:
                self.root.after(100, self._drain_queue)

    root = tk.Tk()
    OrganizerGUI(root)
    root.mainloop()


def run_cli(args):
    with BatchPDFOrganizer(
        downloads_folder=args.downloads,
        ebooks_folder=args.ebooks,
        api_key=args.api_key,
        provider=args.provider,
        dry_run=args.dry_run,
        category_template=args.category_template,
        use_content_analysis=args.content_analysis,
    ) as organizer:
        results = organizer.organize_pdfs()
        if organizer.summary.get("failed"):
            return 1
        return 0 if results or organizer.summary.get("total_files", 0) == 0 else 1


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Batch PDF organizer with CLI and GUI.")
    parser.add_argument("--gui", action="store_true", help="Launch the organizer GUI")
    parser.add_argument(
        "--downloads", default=str(Path.home() / "Downloads"), help="Downloads folder to scan"
    )
    parser.add_argument("--ebooks", help="Ebooks folder destination")
    parser.add_argument(
        "--provider", choices=["gemini", "anthropic", "deepseek"], default="deepseek"
    )
    parser.add_argument("--api-key", help="API key for the selected provider")
    parser.add_argument("--dry-run", action="store_true", help="Preview only; do not move files")
    parser.add_argument("--category-template", help="Optional category template JSON file")
    parser.add_argument(
        "--content-analysis",
        action="store_true",
        help="Send text previews of unclear files to the AI provider (off by default)",
    )
    parser.add_argument("--no-content-analysis", action="store_true", help=argparse.SUPPRESS)
    return parser


def main(argv=None):
    parser = build_arg_parser()
    argv = sys.argv[1:] if argv is None else argv

    if not argv or "--gui" in argv:
        launch_gui()
        return 0

    args = parser.parse_args(argv)
    if not args.ebooks:
        parser.error("--ebooks is required in CLI mode")
    if not args.api_key:
        parser.error("--api-key is required in CLI mode")
    return run_cli(args)


if __name__ == "__main__":
    raise SystemExit(main())
