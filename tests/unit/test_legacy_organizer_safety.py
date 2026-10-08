"""Untrusted AI output must never move files outside the library or lose log history."""

import json
from pathlib import Path

import pytest

pytest.importorskip("google.genai")
pytest.importorskip("anthropic")
pytest.importorskip("openai")
pytest.importorskip("pypdf")

import organize_batch
from organize_batch import BatchPDFOrganizer


def make_organizer(tmp_path: Path, **kwargs) -> BatchPDFOrganizer:
    downloads = tmp_path / "downloads"
    library = tmp_path / "library"
    downloads.mkdir(exist_ok=True)
    library.mkdir(exist_ok=True)
    return BatchPDFOrganizer(
        downloads, library, require_api_key=False, use_content_analysis=False, **kwargs
    )


def make_source(tmp_path: Path, name: str = "book.pdf") -> Path:
    source = tmp_path / "downloads" / name
    source.parent.mkdir(exist_ok=True)
    source.write_bytes(b"%PDF-1.4\n")
    return source


@pytest.mark.security
@pytest.mark.parametrize(
    "category",
    ["../../escaped", "..\\..\\escaped", "/abs/escaped", "C:/escaped", "C:\\escaped", "a/../../b"],
)
def test_category_cannot_escape_library(tmp_path: Path, category: str) -> None:
    organizer = make_organizer(tmp_path)
    source = make_source(tmp_path)

    organizer.move_pdf({"source": str(source), "filename": source.name, "category": category})

    library = (tmp_path / "library").resolve()
    moved = list(library.rglob("book.pdf"))
    assert len(moved) == 1
    assert moved[0].resolve().is_relative_to(library)
    assert not (tmp_path / "escaped").exists()


@pytest.mark.security
@pytest.mark.parametrize(
    "rename",
    ["../../evil", "C:\\Windows\\evil", "a:stream", "CON", 'bad<>|?*"name', "", "   ", 42],
)
def test_rename_is_sanitised_to_a_plain_pdf_name(tmp_path: Path, rename: object) -> None:
    organizer = make_organizer(tmp_path)
    source = make_source(tmp_path)

    destination = organizer.move_pdf(
        {"source": str(source), "filename": source.name, "category": "Books", "rename_to": rename}
    )

    books = (tmp_path / "library" / "Books").resolve()
    assert destination.parent.resolve() == books
    assert destination.suffix == ".pdf"
    assert not set('<>:"/\\|?*') & set(destination.name)
    assert destination.stem.split(".")[0].upper() not in organize_batch.WINDOWS_RESERVED_NAMES
    assert destination.exists()


def test_nested_category_is_preserved(tmp_path: Path) -> None:
    organizer = make_organizer(tmp_path)
    source = make_source(tmp_path)

    destination = organizer.move_pdf(
        {
            "source": str(source),
            "filename": source.name,
            "category": "Computer & ICT/Programming/Python",
            "rename_to": "Python Guide",
        }
    )

    expected = (
        tmp_path / "library" / "Computer & ICT" / "Programming" / "Python" / "Python Guide.pdf"
    )
    assert destination == expected
    assert expected.exists()


def test_name_collision_never_overwrites(tmp_path: Path) -> None:
    organizer = make_organizer(tmp_path)
    existing = tmp_path / "library" / "Books" / "book.pdf"
    existing.parent.mkdir(parents=True)
    existing.write_bytes(b"original")
    source = make_source(tmp_path)

    destination = organizer.move_pdf(
        {"source": str(source), "filename": source.name, "category": "Books"}
    )

    assert existing.read_bytes() == b"original"
    assert destination.name == "book_1.pdf"


def test_malformed_ai_items_are_normalised() -> None:
    raw = [
        {"number": "2", "category": "Business", "confidence": "high", "rename": None},
        {"number": 1, "category": None, "rename": 7},
        {"number": 99, "category": "Out of range"},
        {"category": "No number"},
        "not a dict",
        {"number": True, "category": "Bool is not a number"},
        {"number": 2.7, "category": "Fractional numbers are rejected"},
        {"number": 2, "category": "Duplicate of item 2"},
    ]

    items = organize_batch.normalise_categorizations(raw, pdf_count=3)

    assert items == [
        {"number": 2, "category": "Business", "confidence": "high", "rename": None},
        {"number": 1, "category": "Uncategorized", "confidence": "low", "rename": "7"},
    ]


def test_one_failed_move_does_not_lose_log_entries(tmp_path: Path, monkeypatch) -> None:
    organizer = make_organizer(tmp_path)
    for name in ("a.pdf", "b.pdf", "c.pdf"):
        make_source(tmp_path, name)
    monkeypatch.setattr(organizer, "load_or_analyze_categories", lambda: {})
    monkeypatch.setattr(
        organizer,
        "batch_categorize_all",
        lambda pdfs, _categories: [
            {"number": i, "category": "Books", "confidence": "high", "rename": None}
            for i in range(1, len(pdfs) + 1)
        ],
    )
    real_move = organizer.move_pdf

    def flaky_move(result):
        if Path(result["source"]).name == "b.pdf":
            raise PermissionError("locked")
        return real_move(result)

    monkeypatch.setattr(organizer, "move_pdf", flaky_move)

    organizer.organize_pdfs()

    log = json.loads((tmp_path / "library" / "organization_log.json").read_text("utf-8"))
    logged = sorted(Path(item["source"]).name for item in log["organized_files"])
    assert logged == ["a.pdf", "c.pdf"]
    assert organizer.summary["moved"] == 2
    assert [Path(item["source"]).name for item in organizer.summary["failed"]] == ["b.pdf"]
    assert (tmp_path / "downloads" / "b.pdf").exists()


def test_corrupt_log_is_preserved_and_replaced(tmp_path: Path) -> None:
    library = tmp_path / "library"
    library.mkdir()
    (library / "organization_log.json").write_text("{truncated", encoding="utf-8")

    organizer = make_organizer(tmp_path)

    assert organizer.log["organized_files"] == []
    backups = list(library.glob("organization_log.corrupt-*.json"))
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == "{truncated"


def test_log_write_is_atomic(tmp_path: Path, monkeypatch) -> None:
    organizer = make_organizer(tmp_path)
    organizer.log["organized_files"].append({"source": "kept.pdf"})
    organizer.save_log()
    log_file = tmp_path / "library" / "organization_log.json"

    def explode(*_args, **_kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(organize_batch.json, "dump", explode)
    organizer.log["organized_files"].append({"source": "new.pdf"})
    with pytest.raises(OSError):
        organizer.save_log()

    assert json.loads(log_file.read_text("utf-8"))["organized_files"] == [{"source": "kept.pdf"}]
    assert list(log_file.parent.glob("*.tmp")) == []


@pytest.mark.parametrize(
    ("provider", "retired"),
    [
        ("gemini", "gemini-1.5-flash"),
        ("anthropic", "claude-3-5-sonnet-20240620"),
        ("deepseek", "deepseek-chat"),
    ],
)
def test_default_models_are_not_retired(tmp_path: Path, provider: str, retired: str) -> None:
    organizer = make_organizer(tmp_path, provider=provider)
    assert organizer.model_name != retired


@pytest.mark.security
def test_content_analysis_is_opt_in(tmp_path: Path) -> None:
    downloads = tmp_path / "d"
    downloads.mkdir()
    organizer = BatchPDFOrganizer(downloads, tmp_path / "lib", require_api_key=False)

    assert organizer.use_content_analysis is False
    assert organizer.content_analyzer is None
    assert organize_batch.build_arg_parser().parse_args([]).content_analysis is False
    assert organize_batch.build_arg_parser().parse_args(["--content-analysis"]).content_analysis


def test_anthropic_default_is_haiku(tmp_path: Path) -> None:
    assert make_organizer(tmp_path, provider="anthropic").model_name == "claude-haiku-5-5"


@pytest.mark.security
@pytest.mark.parametrize(
    ("payload", "expected"),
    [
        ({"use_content_analysis": True}, False),
        ({"use_content_analysis": True, "consent_version": 1}, False),
        ({"use_content_analysis": "yes", "consent_version": 2}, False),
        ({"use_content_analysis": True, "consent_version": 2}, True),
        ([], False),
    ],
)
def test_only_current_explicit_consent_is_honoured(payload, expected: bool) -> None:
    assert organize_batch.saved_content_analysis_consent(payload) is expected
