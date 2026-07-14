# Current State Audit

Status: baseline audit  
Audit date: 2026-07-14  
Repository: `peterbamuhigire/Chwezi-PDF-Suite` at `030a895`  
Scope: tracked source, tests, documentation, installers, assets, Git history, and public GitHub metadata

## Executive finding

The repository is a useful prototype collection, not yet an installable document platform. Its strongest assets are working Markdown extraction for PDF, DOCX, EPUB and PPTX; visual PDF signature placement; an AI-assisted PDF organiser; and a watch-folder prototype. These features are coupled to standalone scripts, inconsistent interfaces and unsafe file-handling assumptions.

The main release blockers are concrete:

- there is no `pyproject.toml`, package namespace, licence file, CI workflow or collected pytest suite;
- four entry paths can install Python packages while running;
- `pdf_to_epub.py` and `pptx_to_epub.py` emit Markdown despite their names;
- web mode runs Flask debug mode on `0.0.0.0`, returns API keys to the browser and stores them in a signed client-side session cookie;
- the web client interpolates AI and file-derived values into `innerHTML`, creating a reachable cross-site scripting path;
- AI-proposed categories and filenames reach `shutil.move()` without containment or filename validation;
- converters overwrite existing output and can leave an empty placeholder after failure;
- the organiser may send extracted document text to an external AI provider without an explicit per-job consent control.

## Inspection evidence

The audit inspected all 23 Python files, 4 web assets, 18 project documentation files, 4 historical plan/spec files, 3 installation/launch scripts, `requirements.txt`, `category_template.json`, Git history, and the repository's embedded skill files. Generated caches were identified but excluded from behavioural review.

Commands included:

```text
rg --files -uu -g '!**/.git/**'
python -m compileall -q -f .
python -m pytest -q test_pdf_to_epub.py test_pptx_to_epub.py test_signature.py
python test_pdf_to_epub.py
python test_pptx_to_epub.py
python test_signature.py
git log --oneline --stat -12
```

The standalone converter and signature scripts pass: PDF/DOCX/EPUB-to-Markdown 2/2, PPTX-to-Markdown 1/1, visual-signature checks 10/10. Pytest collected no tests and then failed because the legacy scripts close pytest's captured stream. PyMuPDF-specific rotation coverage was skipped because the imported `fitz` module did not expose the expected PyMuPDF API.

## Repository map

| Path | Observed responsibility | Assessment |
|---|---|---|
| `organize_batch.py` | AI categorisation, keyword fallback, file moves, Tk GUI and CLI | Working prototype; 825-line mixed-responsibility module |
| `pdf_content_analyzer.py` | PDF metadata/text previews and filename heuristics | Useful; parser errors are reduced to strings |
| `pdf_to_epub.py` | PDF, EPUB, DOCX and DOC to Markdown | Working but misnamed; overwrites output and auto-installs dependencies |
| `pptx_to_epub.py` | PPTX to slide-preserving Markdown | Working but misnamed; overwrites output and auto-installs dependencies |
| `pdf_signature.py` | Visual image stamping, filters, batch mode, Tk UI | Valuable; not cryptographic signing; dictionary results and broad exception handling |
| `sign_setup.py` | Interactive signature launcher | Duplicates validation and attempts runtime installation |
| `watch_organizer.py` | Debounced watch-folder AI organisation | Partial; no durable queue, retries, recovery or safe shutdown of timers |
| `watch_setup.py` | Interactive watch launcher | Attempts runtime installation and exposes key fragments on screen |
| `web_interface.py` | Flask organiser and visual-signature UI | Functional local prototype with critical security defects |
| `templates/index.html` | Single-page Flask UI | Label coverage is partial; no semantic navigation or live status regions |
| `static/js/app.js` | UI state and API calls | Duplicates workflow logic and contains unsafe `innerHTML` rendering |
| `static/css/style.css` | Responsive styling | Has one breakpoint; removes focus outlines; no dark/high-contrast theme |
| `index-app.py` | CustomTkinter launcher | Product launcher, not a unified desktop app; contains `shell=True` path |
| `git_puller.py` | Textual UI for updating unrelated Git repositories | Out of product scope; should move to another project or optional developer tool |
| `dependency_bootstrap.py` | Installs missing packages at import time | Must be retired from runtime use |
| `setup.py` | Interactive installer/configuration wizard | Misleading name; not packaging metadata; stores settings under a legacy name |
| `diagnose.py` | Ad-hoc environment checks | Useful intent; imports application code and lacks a stable machine-readable contract |
| `fetch-categories.py` | Builds a category template from a library tree | Useful migration candidate |
| `install.ps1`, `install.sh` | System Python and dependency installers | High privilege/supply-chain surface; not package-manager based |
| `run_gui.sh` | Legacy organiser launcher | Compatibility wrapper candidate |
| root `test_*.py` | Standalone diagnostic scripts | Behavioural evidence, not a collected automated suite |
| `tests/` | Only generated `__pycache__` files | No tracked test code |
| `docs/` | User guides and historical plans | Contains obsolete names, encoding damage and contradictory privacy claims |
| `skills/` | Embedded generic skill authoring material | Not part of the document product; preserve until ownership is decided |
| `category_template.json` | Large pre-generated personal taxonomy | Useful example shape; content and provenance need review before distribution |

## Current feature matrix

| Feature | State | Evidence and limitation |
|---|---|---|
| PDF to Markdown | Working, unvalidated | Extracts lines, headings, lists and basic code heuristics; no OCR, image or table model |
| DOCX to Markdown | Partial | Parses OOXML directly; table output lacks a Markdown header separator; archive limits absent |
| legacy DOC to Markdown | Partial, platform-dependent | LibreOffice or Word COM; subprocess lacks timeout and Word automation is Windows-only |
| EPUB to Markdown | Partial, security-sensitive | Reads spine XHTML; no archive expansion limits; limited HTML semantics |
| PPTX to Markdown | Working, partial fidelity | Preserves slide boundaries, text and simple tables; omits images, notes and charts |
| batch conversion | Partial | Recurses and continues after errors; no typed per-file result, cancellation or collision policy |
| PDF visual signature | Working | PNG placement, page filters, opacity and rotation; this is visual stamping only |
| cryptographic signing | Absent | No certificate signing or validation |
| AI organisation | Working prototype | Gemini, Anthropic and DeepSeek; remote content disclosure is insufficiently controlled |
| local rule organisation | Partial | Small hard-coded filename keyword map only |
| watch folder | Partial | Debounce and two-point size check; no persistence, duplicate detection or retry policy |
| web UI | Partial, unsafe | Upload, organise, browse and sign; no job model or file isolation |
| desktop UI | Duplicated prototypes | Tk, CustomTkinter and Textual surfaces; no common navigation or service layer |
| CLI | Inconsistent | Per-script argparse contracts; no `chwezi` command or JSON result standard |
| Python API | Absent | Public behaviour is exposed through script classes and dictionaries |
| job history | Absent | JSON operation logs contain full paths but no durable job state |
| OCR/PDF toolkit | Mostly absent | No merge, split, compression, security inspection, OCR or structured extraction services |

## Structural findings

### Duplicate logic and tight coupling

- GUI, CLI, web and watch paths construct organiser inputs and categorisation maps separately.
- Settings, dependency checks, error presentation and file discovery are repeated.
- `organize_batch.py`, `pdf_signature.py` and both converters combine domain work, interface code and filesystem effects.
- External SDK clients are created directly in the organiser constructor, preventing isolated tests.

### Dead, obsolete and misleading material

- `pending_pdfs` and `signature_uploads` in `web_interface.py` are unused.
- `_get_processed_signature_bytes()` has no observed caller.
- `test_basic.py` is interactive despite its test name.
- `git_puller.py` and its 1,500-line historical plan are unrelated to the product mission.
- documentation still refers to absent `.bat` files and claims the web interface is local-only while it binds all interfaces.

### Security and privacy

| Severity | Finding | Evidence |
|---|---|---|
| Critical | AI-controlled destination traversal | `organize_batch.py` joins unvalidated `category` and `rename_to` values before `shutil.move()` |
| Critical | Stored/reflected DOM XSS path | `static/js/app.js` writes AI categories, renames and filesystem values through template-string `innerHTML` |
| High | Unsafe development server exposure | `web_interface.py` uses `debug=True`, `host='0.0.0.0'` |
| High | Client-side secret exposure | API key is stored and returned through Flask's cookie-backed session |
| High | Unauthorised source path selection | API accepts client-supplied `path` values and checks only existence |
| High | Archive-bomb exposure | DOCX/EPUB ZIP members are read without entry, size or compression-ratio limits |
| Medium | Remote content disclosure | organiser includes extracted text previews in remote AI prompts for some files |
| Medium | Command/process risk | launcher uses `shell=True`; LibreOffice conversion has no timeout |
| Medium | Upload isolation and retention | shared predictable folders and filenames allow collisions; no cleanup policy |
| Medium | Sensitive logging | organisation/signature logs retain full source, output and signature paths |

No committed credential pattern was found in the reviewed source. This was a static review, not a penetration test.

### Data-loss and temporary-file risks

- Conversion outputs are overwritten without warning.
- `pdf_to_epub.py` touches the final output before conversion; failure can leave an empty file.
- Organisation moves inputs directly, with no transaction, undo manifest, rollback or fsync boundary.
- Batch signing can recurse into its own output directory on later runs.
- Web uploads collide on sanitised filenames and persist indefinitely in a shared home-directory folder.
- JSON logs are rewritten non-atomically and corruption is sometimes silently discarded.

### Performance and reliability

- PDF extraction loads all extracted lines into memory; web browsing repeatedly walks the whole library.
- Organisation sends large category lists and up to 150 documents per remote prompt without a request-size estimator.
- Watch mode sleeps in its timer thread and does not reschedule files found unstable unless another event arrives.
- No bounded worker pool, cancellation token, memory/page limits or benchmark harness exists.
- Broad exception handling converts programming faults into strings and makes failure classification impossible.

### Packaging, dependency and licensing

- `requirements.txt` installs every interface and three cloud SDKs together.
- `PyMuPDF` is used opportunistically but is absent from requirements; the installed `fitz` name can resolve to the wrong distribution.
- There is no lock file, lower/upper compatibility policy, third-party notice or licence.
- Current PyPI metadata describes PyMuPDF as AGPL-3.0 or commercial; bundling it requires a deliberate licensing decision.
- Public GitHub metadata returned no detected licence on 2026-07-14.

### Cross-platform risks

- Word COM and `pywin32` are Windows-specific.
- Windows launch quoting uses a shell; Unix scripts assume distro package managers and privilege escalation.
- path length, reserved device names, case-insensitive collisions and symlinks are not handled.
- GUI behaviour has no platform matrix evidence.

## Features to preserve

1. The existing Markdown heuristics and slide-boundary output, protected by characterisation tests.
2. Visual signature placement semantics, including A4-relative scale and rotated-page behaviour.
3. Provider choice and the local keyword fallback, moved behind explicit classifier interfaces.
4. Dry-run organisation and category-template support.
5. Watch-mode batching as a user concept, redesigned around durable jobs and file-stability policy.
6. The browser-based review step before moving AI-classified files.

## Audit limits

- No representative confidential or 500 MB corpus was available; large-file claims are untested.
- No macOS/Linux execution environment was available in this cycle.
- Public GitHub reported no open issues or pull requests; there was no external defect backlog to reconcile.
- Dependency vulnerability and licence conclusions require a locked dependency set before release.

