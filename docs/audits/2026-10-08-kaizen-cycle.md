# Kaizen cycle — 2026-10-08

| Field | Value |
|---|---|
| Scope | Whole repository; focus on the legacy root applications users actually run |
| Baseline commit | `8ff347d` |
| Method | Observe → baseline → select → experiment → check → standardise (engineering `kaizen-improvement-system`) |
| Reviews | Three read-only reviews (security, silent failure, documentation drift) and two independent diff reviews |
| Next re-audit | 2026-11-08, or sooner if `organize_batch.py`, `web_interface.py`, `watch_organizer.py` or `documents_to_markdown.py` change |

## 1. Observation

The packaged core (`src/chwezi_docs`) was already healthy: ruff clean, mypy strict clean, 37 tests,
90% branch coverage. The roughly 8,000 lines of root legacy modules (organiser, web UI, watcher,
signer, converter), which are what the launchers and frozen executables run, were **outside every
CI gate**. Ruff reported 190 findings on them, none of their behaviour had a collected test, and
the desktop build could not start because its generated files were stale.

## 2. Scorecard

Repository policy publishes `min(raw, 65)`. Every score cites evidence. Unrun checks are marked
NOT ASSESSED rather than folded into a number.

| Dimension | Raw before | Raw after | Evidence and remaining deficiency |
|---|---:|---:|---|
| Security and privacy | 20 | 62 | Before: AI output and browser JSON could move or delete any file; the API key went to the browser; archives were unbounded; document text went to remote AI by default. After: containment, id-only file access, Host and Origin checks, session eviction, archive limits, and opt-in consent, each with red/green tests. Still missing: web authentication, a per-run preview and audit trail of what is sent, and symlink policy inside the library beyond the resolve check. |
| Correctness and reliability | 35 | 60 | Thirteen verified defects fixed with regression tests (§4). Not yet tested: GUI flows by hand, and watch mode against a real browser download. |
| Currentness | 20 | 60 | All three default AI models were retired, so default runs on every provider failed. New IDs are verified against provider documentation (§5). A live API call is NOT ASSESSED (no key used). |
| Test evidence | 40 | 62 | 37 → 104 collected tests, plus 1 PyMuPDF test skipped where PyMuPDF is absent. Legacy line coverage is not measured. |
| Delivery gates | 45 | 62 | The whole repository (excluding the embedded `skills/`) passes the full ruff configuration, and CI enforces it. CI runs the legacy tests with their dependencies installed. The desktop build is repaired and verified locally. GitHub Actions has not run on this commit. |
| Documentation accuracy | 35 | 60 | Mojibake removed; product names, classes, scripts, pins, models, consent behaviour, API contract and packager path corrected; unsourced dollar figures replaced by API-call counts; no broken relative links outside `skills/`. |
| Desktop packaging | 20 | 58 | Before: the build aborted on a manifest-hash mismatch. After: an unsigned development build produces four executables and a 71.9 MB zip; the frozen organiser passed a headless dry run. Interactive GUI smoke tests are `manual-check-required`; installer and signing are NOT ASSESSED. |
| Accessibility and UX | — | — | NOT ASSESSED beyond the design-slop static pass (0 findings, 4 evidenced waivers). |
| **Published (capped)** | **31** | **61** | Unweighted mean of the assessed rows. |

## 3. Evidence register

| Check | Command | Result |
|---|---|---|
| Tests (unit, regression, security) | `python -m pytest -q` | 104 passed, 1 skipped |
| Core coverage | `python -m pytest --cov=chwezi_docs` | ≥ 85% gate met (90%) |
| Lint, whole repository | `ruff check . --extend-exclude skills` | pass |
| Core format and types | `ruff format --check src tests`; `mypy src/chwezi_docs` | pass |
| Legacy script suites | `python test_signature.py`; `python test_documents_to_markdown.py` | 10/10; 4/4 |
| Locked desktop build | `scripts/build-desktop-suite.ps1 -UnsignedDevelopmentBuild -SkipInstaller` | 95 passed in the locked env; 4 executables; zip SHA-256 `e178f49d…5e4d3a45` |
| Frozen-binary smoke | `ChweziOrganizer.exe --dry-run` on an empty folder | exit 0 |
| Design static pass | `chwezi-slop` on `templates/index.html`, `static/css/style.css` | 0 findings, 4 waived with evidence |
| Red/green proof | New tests run against the pre-fix code | Organiser safety 22/22 failed before; web security 6/8 failed (2 controls); watch, analyser, signer, converter 10/12 failed (2 controls); archive bomb and entity tests failed; nested-library and DNS-rebinding tests fail with their guard removed |
| Path escape reproduced | `test_category_cannot_escape_library` on old code | The PDF was moved outside the library for every hostile category |

Negative evidence kept:
- A `ruff --fix` pass deleted the import that `setup.py`'s self-test exists to perform. This was
  caught in diff review and restored with an explicit `noqa`.
- A documentation sub-agent wrongly reported two files as already git-ignored. This was caught
  before commit, and the one per-user file was ignored explicitly.
- Regenerating the packaging silently reverted the per-app icon override. This was caught by
  diffing and restored, and the pitfall is now documented in `DESKTOP_DISTRIBUTION.md`.
- The lint pass turned `diagnose.py`'s Python version check into an unconditional "OK". The second review caught it and the check was restored for 3.11+.
- The first build attempt hit a transient lock on `base_library.zip` (the retry succeeded with
  no stage process running).

## 4. Improvement actions

| ID | Root cause | Change | Acceptance evidence |
|---|---|---|---|
| E1 | Untrusted AI and browser values reached `shutil.move` and `unlink` | `sanitize_path_segment`, `safe_category_path`, `safe_pdf_filename`, and a resolved-root check in `move_pdf`; web uploads addressed by server-issued uuid; key held server-side; loopback Host allowlist and Origin check on writes; `SameSite=Strict`; idle-session eviction deletes abandoned uploads and tolerates locked files | `test_legacy_organizer_safety.py`, `test_legacy_web_security.py` |
| E2 | Retired model IDs hard-coded | `DEFAULT_MODELS`: `gemini-3.8-flash`, `claude-haiku-5-5` (low effort, no sampling parameters, 16k `max_tokens` because thinking shares the budget), `deepseek-flash` | `test_default_models_are_not_retired`, `test_anthropic_default_is_haiku` |
| E3 | Organiser run aborted on one bad file; non-atomic, crash-prone log; unvalidated AI items | Per-file isolation and `summary["failed"]`; non-zero CLI exit; atomic `save_log`; corrupt log preserved aside; `normalise_categorizations` (rejects fractional, duplicate and out-of-range numbers) | Organiser safety tests |
| E4 | Watch mode handled only `on_created`, stranded growing files, could overlap batches, and could re-queue its own moves | `on_moved`, timer re-arm, `processing_lock`, library-path exclusion, `batch_delay ≥ 1`, per-file isolation, log entries recorded | `test_legacy_watch.py` |
| E5 | Smaller defects | Random-case gibberish check, batch-sign output pruning, output-equals-input guard, corrupt signature log handling, no empty `.md` on failure, `soffice` timeout, settings-load failures surfaced, setup scripts survive corrupt settings and bad input | `test_legacy_content_analyzer.py`, `test_legacy_signature_batch.py`, `test_legacy_markdown_failure.py` |
| E6 | R-005: unbounded archive reads | `open_checked_archive`, `read_archive_member`, `parse_untrusted_xml`; the entity scan decodes UTF-16/32 first (a bypass the second review demonstrated) | `test_legacy_archive_limits.py` |
| E7 | R-011: text previews sent to remote AI by default | Off by default on every path; explicit GUI and web checkboxes, `--content-analysis` flags, and a `watch_setup.py` prompt; opt-ins saved before this change are not honoured (`consent_version`); API keys masked to the last four characters, or fully when short | Consent tests in the organiser, watch and web suites |
| E8 | Desktop build blocked by a stale manifest hash | Regenerated with the canonical packager; per-app icon override preserved; `.gitattributes` pins the manifest to CRLF so the byte hash is stable on every checkout; stale packager path corrected in the docs | Locked build and frozen smoke run |
| E9 | Documentation drift and repository hygiene | `CLAUDE.md` and the guides repaired; scratch `_test_stamp.py` replaced by an integration test; stale `DOCUMENTATION_UPDATE_SUMMARY.md` removed; per-user `.claude/settings.local.json` untracked and ignored | Link and mojibake sweep |
| E10 | Legacy code was ungated | Whole repository passes full ruff; CI installs `.[dev,suite]` and runs `ruff check . --extend-exclude skills`; pytest `pythonpath` set so tests run from a fresh checkout | `.github/workflows/quality.yml`, `pyproject.toml` |
| E11 | Design-slop findings in the web UI | Filler kicker and its 11.5 px style removed; warm-paper ground, folder-tree guide and toast status stripe waived with cited evidence | `chwezi-slop` pass |

Rollback: each action is confined to the files named above and can be reverted per file. The web
API contract changed (`has_api_key` replaces `api_key`; responses no longer carry `path`; settings
gained `content_analysis`), so `static/js/app.js`, `templates/index.html` and `web_interface.py`
must be reverted together.

## 5. Currentness record

| Claim | Source | Checked |
|---|---|---|
| `gemini-1.5-flash` shut down 2025-09-29; current stable IDs include `gemini-3.8-flash` | <https://ai.google.dev/gemini-api/docs/changelog>, <https://ai.google.dev/gemini-api/docs/models> | 2026-10-08 |
| `claude-3-5-sonnet-20240620` retired 2025-10-28; `claude-haiku-5-5` is current, accepts `output_config.effort`, rejects non-default sampling parameters | Anthropic model reference bundled with the Claude API skill (cached 2026-10-06); installed `anthropic` 0.97.0 exposes `output_config` | 2026-10-08 |
| `deepseek-chat` deprecated 2026-07-24; current names are `deepseek-flash` and `deepseek-v4-pro` | <https://api-docs.deepseek.com/>, <https://api-docs.deepseek.com/quick_start/pricing> (the deprecation date comes from secondary reporting of DeepSeek's earlier notice) | 2026-10-08 |
| `actions/checkout@v7` exists (v7.0.1, 2026-07-20) | GitHub releases API | 2026-10-08 |

## 6. Re-audit handoff

1. Run the GitHub Actions matrix on this commit; it is the only unverified gate.
2. Do the interactive GUI smoke checks the build marks `manual-check-required` (launcher,
   organiser, signer, Markdown converter), in light and dark mode.
3. Make one live, low-cost categorisation call per provider to confirm the new model IDs end to end.
4. R-011 follow-up: add a preview of exactly what will be sent, and an audit-trail entry per run.
5. Web adapter: still local-only and unauthenticated; keep it off any network interface.
6. Make archive limits configurable once the `chwezi_docs` converter contracts absorb the legacy
   converter.
