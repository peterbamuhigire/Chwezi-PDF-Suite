# Migration Plan

## Strategy

Use a strangler migration: establish typed package seams, route new interfaces through them, then move one proven behaviour at a time. Legacy entrypoints remain wrappers until their replacement has characterisation, unit and interface tests.

## Compatibility rules

- Do not remove a legacy script in the first public release.
- Preserve default visual-signature placement semantics.
- Preserve Markdown structure where a golden fixture records it; intentional changes require a migration note.
- Replace runtime installation with an actionable missing-capability error.
- Keep source files unchanged by default; correcting destructive legacy defaults may change behaviour immediately because it is a safety fix.

## Migration sequence

1. Add `pyproject.toml`, `src/chwezi_docs`, version and test configuration.
2. Add domain formats, status, errors, requests, results and collision policy.
3. Add capability registry/planner and `chwezi capabilities`.
4. Wrap existing file-to-Markdown converters through a conversion service with staging and validation.
5. Convert legacy CLI modules into deprecation wrappers while retaining GUI access temporarily.
6. Extract visual signature placement into `signature_service`; keep `pdf_signature.py` as wrapper.
7. Extract organisation classification from safe filesystem movement; block traversal and add undo manifests.
8. Introduce job persistence, then move watch and UI operations onto jobs.
9. Replace the unsafe Flask adapter after application contracts stabilise.
10. Retire old launchers only after one documented release cycle and usage review.

## Data migration

| Legacy data | New location/model | Treatment |
|---|---|---|
| `~/.pdf_organizer_settings.json` | platform user config | import once; never copy plaintext keys without consent |
| `organization_log.json` | job/event store plus undo manifest | read-only importer; preserve original |
| `category_template.json` | versioned organisation rules/preset | validate schema and paths before import |
| web upload folders | job-specific data directory | offer cleanup command; do not auto-delete unknown user data |
| signature logs | job history | import metadata only; redact full paths by default |

## Legacy mapping

| Legacy entrypoint | New command | Initial status | Removal condition |
|---|---|---|---|
| `pdf_to_epub.py` | `chwezi convert FILE --to markdown` | deprecated wrapper after parity | two releases after parity |
| `pptx_to_epub.py` | `chwezi convert DECK.pptx --to markdown` | deprecated wrapper after parity | two releases after parity |
| `organize_batch.py` | `chwezi organise PATH` | preserved until safe mover/classifier migration | P1 parity |
| `pdf_signature.py` | `chwezi sign FILE --signature IMAGE` | preserved; label as visual | P1 parity |
| `watch_organizer.py` | `chwezi watch PATH --workflow NAME` | preserved until durable job recovery | P1 parity |
| `web_interface.py` | `chwezi web` | security-blocked for network use | local FastAPI replacement |
| `index-app.py` | `chwezi desktop` | preserved during desktop transition | PySide6 feature parity |

## Rollback

Foundation changes are additive. A release can revert package entrypoints while legacy scripts remain. Data migrations write a new store and never modify legacy logs. Converter promotion occurs only after validation; staging directories are safe to remove after a failed job.

## Migration gates

- characterisation fixture exists before moving an algorithm;
- new service produces typed result and stable error codes;
- legacy and new entrypoints share the same application service;
- documentation names unsupported and partially supported cases;
- rollback/cleanup path is tested;
- a deprecation warning points to an implemented command, not a future placeholder.

