"""Regression tests for the legacy watch-mode handler."""

import sys
import types
from pathlib import Path
from typing import ClassVar

import pytest

pytest.importorskip("watchdog")

import watch_organizer


class FakeTimer:
    started: ClassVar[list] = []

    def __init__(self, interval, function):
        self.interval = interval
        self.function = function

    def start(self):
        FakeTimer.started.append(self)

    def cancel(self):
        pass


@pytest.fixture
def watcher(tmp_path, monkeypatch):
    FakeTimer.started = []
    monkeypatch.setattr(watch_organizer.threading, "Timer", FakeTimer)
    monkeypatch.setattr(watch_organizer.time, "sleep", lambda _s: None)
    return watch_organizer.PDFWatcher(tmp_path, tmp_path / "ebooks", "key", "gemini", batch_delay=1)


def _moved(src, dest, is_directory=False):
    return types.SimpleNamespace(src_path=str(src), dest_path=str(dest), is_directory=is_directory)


def test_on_moved_queues_renamed_pdf(watcher, tmp_path):
    dest = tmp_path / "book.pdf"
    watcher.on_moved(_moved(tmp_path / "book.pdf.crdownload", dest))

    assert dest in watcher.pending_pdfs
    assert len(FakeTimer.started) == 1


def test_on_moved_ignores_non_pdf_and_directories(watcher, tmp_path):
    watcher.on_moved(_moved(tmp_path / "a.part", tmp_path / "a.zip"))
    watcher.on_moved(_moved(tmp_path / "x", tmp_path / "folder.pdf", is_directory=True))

    assert not watcher.pending_pdfs
    assert FakeTimer.started == []


def test_moves_into_a_nested_library_are_ignored(watcher, tmp_path):
    library_file = tmp_path / "ebooks" / "Books" / "book.pdf"
    library_file.parent.mkdir(parents=True)
    library_file.write_bytes(b"%PDF-1.4")

    watcher.on_moved(_moved(tmp_path / "book.pdf", library_file))

    assert not watcher.pending_pdfs
    assert FakeTimer.started == []


def test_growing_file_rearms_timer(watcher, tmp_path, monkeypatch):
    pdf = tmp_path / "grow.pdf"
    pdf.write_bytes(b"%PDF-1.4")

    def grow(seconds):
        if seconds == 0.5:
            with pdf.open("ab") as handle:
                handle.write(b"more")

    monkeypatch.setattr(watch_organizer.time, "sleep", grow)
    watcher.pending_pdfs.add(pdf)

    watcher._process_pending_pdfs()

    assert pdf in watcher.pending_pdfs
    assert len(FakeTimer.started) == 1


def test_one_failed_move_does_not_abort_batch(watcher, tmp_path, monkeypatch):
    pdfs = []
    for name in ("a.pdf", "b.pdf", "c.pdf"):
        path = tmp_path / name
        path.write_bytes(b"%PDF-1.4")
        pdfs.append(path)
        watcher.pending_pdfs.add(path)
    moved = []
    logged = []

    class FakeOrganizer:
        def __init__(self, **_kwargs):
            self.log = {"organized_files": []}
            self.saved = False

        def __enter__(self):
            return self

        def __exit__(self, *_exc):
            return False

        def get_pdf_info(self, path):
            return {"path": path, "filename": Path(path).name}

        def load_or_analyze_categories(self):
            return []

        def batch_categorize_all(self, pdf_list, _categories):
            return [{"number": i, "category": "X"} for i in range(1, len(pdf_list) + 1)]

        def move_pdf(self, result):
            if result["filename"] == "b.pdf":
                raise ValueError("unsafe destination")
            moved.append(result["filename"])
            return Path("library") / result["filename"]

        def save_log(self):
            self.saved = True
            logged.extend(item["filename"] for item in self.log["organized_files"])

    fake = types.ModuleType("organize_batch")
    fake.BatchPDFOrganizer = FakeOrganizer
    monkeypatch.setitem(sys.modules, "organize_batch", fake)

    watcher._process_pending_pdfs()

    assert len(moved) == 2
    assert watcher.stats["successful"] == 2
    assert watcher.stats["failed"] == 1
    assert sorted(logged) == sorted(moved)


def test_watch_content_analysis_is_opt_in(watcher):
    assert watcher.content_analysis is False
