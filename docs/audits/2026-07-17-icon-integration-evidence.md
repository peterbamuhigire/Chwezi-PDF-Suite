# Chwezi Document Suite icon integration evidence

## 1. Artifact identity

| Field | Value |
|---|---|
| Project | Chwezi Document Suite / `pyPDFLibrarianSort` |
| Deliverable | Supplied SVG icon catalog integrated into the web and desktop applications |
| Owner | Peter Bamuhigire |
| Reviewer | Codex implementation review |
| Date | 2026-07-17 |
| Related skills | `skills-web-dev/SKILL.md`; `python-modern-standards`; `javascript-modern`; `anti-ai-slop`; `ai-slop-audit` |

## 2. Decision record

| Decision | Rationale | Alternatives rejected | Reversal trigger |
|---|---|---|---|
| Keep project-owned copies under `static/icons` | Web templates, frozen desktop apps, and tests need one stable asset root; the purchased originals in Downloads remain untouched. | Runtime dependency on Downloads; copying icons into individual app folders. | The suite adopts a versioned external asset package with a stable runtime contract. |
| Generate light/dark PNGs and multi-size ICOs from the SVG sources | Tk and Windows executable metadata do not consume SVGs consistently; deterministic derivatives preserve theme and packaging support. | Platform-specific ad-hoc conversion at runtime; emoji/text placeholders. | Desktop frameworks gain reliable native SVG and executable-icon support. |
| Resolve desktop icons through `ui_icons.py` | One safe resolver and cache gives all desktop apps consistent theme switching and graceful fallback. | Repeated path/Pillow logic in each application. | The applications move to a UI framework with a shared first-party asset pipeline. |
| Give the suite, organizer, signer, and converter distinct app icons | Windows taskbar/title-bar identity should match the launcher card and user task. | One suite icon for every executable. | Product branding intentionally consolidates all tools into one executable identity. |
| Override the generated PyInstaller spec with per-app icon paths | The current canonical generator applies the product icon to every executable, while the manifest now records each desired icon. | Accepting identical executable icons. | The generator natively honors each `applications[].icon` value; the contract test will then be updated with it. |
| Repair unresolved `chweziGradient` references only in project copies | Forty-six supplied SVGs referenced an undefined gradient and would render incorrectly. | Mutating the purchased originals; allowing browser-dependent broken paint fallback. | Corrected upstream assets are supplied and verified equivalent. |

## 3. Contract evidence

| Contract | Evidence | Location | Pass/fail |
|---|---|---|---|
| Icon catalog | 89 SVG sources; every `url(#...)` target resolves; no SVG contains a script element | `static/icons`; `scripts/build_icon_assets.py`; unit test | Pass |
| Theme raster contract | Every source has a non-empty light and dark PNG derivative | `static/icons/raster`; unit test | Pass |
| Web asset contract | Every icon URL declared by the stylesheet resolves inside the icon root | `static/css/style.css`; unit test | Pass |
| Desktop packaging contract | Manifest and PyInstaller spec map four executables to four existing ICO files | `packaging/desktop-suite.toml`; generated spec; unit test | Pass |

## 4. Test evidence

| Layer | Required evidence | Result |
|---|---|---|
| Unit | Icon, theme, launcher, and packaging checks | Pass: `10 passed` in the focused suite |
| Integration | Full project regression suite | Pass: `35 passed` |
| Static Python | Ruff on changed icon/desktop modules and Python compilation | Pass |
| Static JavaScript | `node --check static/js/app.js` | Pass |
| Security | Local validation rejects SVG scripts, unresolved paint references, and resolver path traversal | Pass: 89 SVGs validated |
| Accessibility/frontend | Existing light/dark contrast tests plus live browser inspection | Pass: all visible web icons rendered in both themes; no console warnings/errors |
| Native desktop | Unsigned PyInstaller verification build and visual inspection of launcher, signer, and converter | Pass for icon integration and app identity; not a release-signing result |

Commands used:

```text
python -X utf8 scripts/build_icon_assets.py --validate-only
uv run --locked python -m pytest tests/unit/test_desktop_suite_ui.py -q
uv run --locked python -m pytest -q
uv run --locked ruff check ui_icons.py index-app.py signature_gui.py scripts/build_icon_assets.py tests/unit/test_desktop_suite_ui.py
uv run --locked python -m py_compile ui_icons.py index-app.py signature_gui.py documents_to_markdown.py scripts/build_icon_assets.py
node --check static/js/app.js
```

## 5. Operational evidence

| Area | Evidence | Release blocker |
|---|---|---|
| Build reproducibility | Icon builder and catalog tests are committed; desktop manifest hash was regenerated | No source-integration blocker |
| Runtime fallback | Missing/invalid desktop assets return no image rather than crashing the app | No |
| Rollback | Remove the icon bindings and `static/icons`; no data migration or user document format changed | No |
| External distribution | Packager doctor reports the declared `LICENSE` file missing; signing is required; Inno Setup is not installed | Yes, for a public installer/release |

## 6. Source and currency evidence

The supplied icon directories are the sole visual source. No web-sourced assets were added. `static/icons/README.md` records their origin and the requirement to retain the subscription/vendor license and purchase evidence before redistribution.

## 7. Anti-slop gate

- Icons are mapped to concrete actions and states rather than added as decoration everywhere.
- Each application has a distinct identity icon and consistent theme-aware controls.
- Dynamic web markup escapes filenames, categories, and messages in the touched rendering paths.
- Asset counts, paint references, paths, package mappings, and live rendering are testable rather than asserted in prose.
- A native visual check caught and corrected image-dependent Tk button sizing in the signer.

Verdict: Pass for the implemented scope.

## 8. Release verdict

| Gate | Verdict | Reviewer note |
|---|---|---|
| Architecture | Pass | Shared resolver and deterministic derivatives avoid per-app asset drift. |
| Security | Pass | SVG scripts, unresolved paint references, and path traversal are checked. |
| Reliability | Pass | Full regression suite passes; missing icon assets degrade safely. |
| Data | Pass | No user data or document-format change. |
| Docs/runbook | Pass for source integration | Provenance and rebuild command are documented. |
| Anti-slop | Pass | Visual and automated evidence supports the result. |

Final decision: **ship the source integration; hold external release packaging** until the project license, icon redistribution evidence, code signing, and installer compiler are present.
