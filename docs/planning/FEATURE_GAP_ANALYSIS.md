# Feature Gap Analysis

Baseline: commit `030a895`  
Target: first credible public release of Chwezi Document Suite

## Priority summary

P0 work is dominated by safety and cohesion, not feature count. Existing conversion and signature behaviour should be wrapped, characterised and corrected before adding a large PDF tool catalogue.

| Capability | Current | P0 target | Priority | Exit evidence |
|---|---|---|---|---|
| Package/API | Flat scripts | `chwezi_docs`, typed requests/results, `DocumentSuite` | P0 | clean wheel install and API tests |
| CLI | Per-script argparse | `chwezi` with stable exits and JSON | P0 | functional CLI tests |
| Safe output | overwrite/touch/move | collision policy, staging, validation, atomic promotion | P0 | failure and traversal tests |
| Capability registry | none | honest source-target and requirement matrix | P0 | graph and detection tests |
| Existing Markdown extraction | working heuristics | shared converter adapters and warnings | P0 | golden Markdown fixtures |
| Visual signature | working script | shared service, typed result, explicit visual label | P0 | regression corpus |
| Core PDF operations | absent | merge, split, extract, rotate, reorder, metadata | P0 | semantic PDF tests |
| Configuration/logging | ad hoc JSON/print | typed precedence and privacy-aware structured logs | P0 | precedence/redaction tests |
| Testing/CI | standalone scripts | pytest, static checks, three-OS matrix | P0 | passing required checks |
| Documentation/licensing | contradictory/no licence | actual-state docs, licence decision, notices | P0 | release checklist |
| Desktop | several launchers | PySide6 shell over application services | P1 | keyboard/accessibility/manual QA |
| OCR/extraction | no OCR, basic text | OCR modes, structured JSON, tables/images | P1 | representative corpus |
| Jobs/watch/workflows | timer prototype | persisted jobs, validated workflow schema, recovery | P1 | restart/retry tests |
| Web | unsafe Flask prototype | localhost FastAPI, isolated uploads, job API | P1 | security integration tests |
| Digital signing/PDF-A/redaction | absent | evaluated optional capabilities | P2 | standards validation and threat review |

## Format gaps

The current implementation supports only PDF, DOCX, DOC, EPUB and PPTX inputs to Markdown. It has no declared output support beyond Markdown and visually stamped PDF. PDF/A, images, OpenDocument, spreadsheets, HTML, RTF, CSV and plain text are unimplemented. The registry must label routes unsupported until tested; installing LibreOffice does not by itself prove conversion quality.

## Interface gaps

- Desktop surfaces do not share navigation, job state or settings.
- CLI commands have different arguments and error formats.
- Web routes perform document work synchronously and trust client paths.
- No stable Python import path exists.
- Watch processing bypasses a durable job service.

## Quality gaps

- no file-signature or reopen validation after conversion;
- no OCR detection or page-level warnings;
- no semantic PDF comparison or golden corpus;
- no page, archive, image, memory, duration or batch limits;
- no cancellation or bounded parallelism;
- no sanitised diagnostic bundle;
- no cross-platform evidence outside developer scripts.

## Product gaps

The prototype's useful differentiator is structured Markdown plus organisation, but the product presently presents these as unrelated tools. The release should lead with four connected jobs: convert/extract, PDF operations, organise/watch and visual signing. Digital signatures, advanced editing and enterprise server mode remain explicit future work.

## Additional feature evaluation

| Feature | Value | Complexity/security | Placement |
|---|---|---|---|
| Document/visual diff | High for review workflows | Medium/high; rendering tolerance needed | P2 optional |
| Forms/flattening | Medium | High; data-loss and signature implications | P2 PDF extra |
| Bookmarks/TOC | High and tractable | Medium | late P1 |
| Accessibility/PDF-UA inspection | High differentiation | High standards expertise | P2 specialised extra |
| Barcode/QR | Medium | Low/medium; untrusted payload handling | optional P1 |
| Full-text indexing | High for management | Medium; sensitive index lifecycle | P2 local module |
| Local question answering | Potentially high | Heavy models, privacy and quality claims | separate optional product layer |
| Cloud connectors | Convenience | Credentials, data residency and API churn | optional post-P1 |
| Plugin system | Long-term flexibility | Large attack/compatibility surface | defer until APIs stabilise |

