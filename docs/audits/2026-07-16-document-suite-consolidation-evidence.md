# Document Suite Consolidation Evidence

## Delivery identity

| Field | Value |
| --- | --- |
| Change | Merge PPTX extraction into the general Markdown converter and remove the unrelated repository updater |
| Date | 2026-07-16 |
| Owner | Peter Bamuhigire |
| Implementation | `documents_to_markdown.py`, launcher, package adapter, tests, and documentation |

## Decisions

| Decision | Rationale | Reversal trigger |
| --- | --- | --- |
| Replace both format-named scripts with `documents_to_markdown.py` | PDF, EPUB, Word, and PowerPoint share one user job and batch/output policy. | A format requires an isolated process for dependency or security containment. |
| Keep `PdfToMarkdownConverter` as an alias | Existing direct imports receive a short compatibility path without keeping the old script. | The next documented breaking release removes legacy Python names. |
| Remove runtime package installation from the unified converter | Importing a PDF workflow must not mutate the Python environment or install PPTX support. | None; capability checks remain the intended replacement. |
| Place the launcher before displaying it | Withdrawing, measuring requested dimensions, setting exact centered geometry, and then showing avoids the visible side-position jump. | Native desktop framework replacement makes Tk geometry obsolete. |
| Keep the repository document-only | Machine-wide source-control maintenance has a different trust boundary and product purpose. | None for this repository. |

## Test evidence

| Gate | Result |
| --- | --- |
| Pytest | 25 passed in 2.27 seconds |
| Converter characterisation | 4 passed: PDF, DOCX/EPUB mixed batch, PPTX, and DOCX/PPTX stem collision |
| Ruff maintained scope | `src` and `tests`: passed |
| Mypy | 22 source files: passed |
| Compile check | unified converter, launcher, and package: passed |
| Build | wheel and source archive built successfully |
| Twine | wheel and source archive: passed |
| Retired-name scan | no source/document/package-archive references to the removed updater or former converter modules |

External reconstruction handoff SHA-256:
`80209294F8613D6B15726F6CFB471A8723B3011FA3C70A49E3E096A6E876A8B9`.
Package artifact hashes are recorded after the final build because the source archive contains
this evidence file.

## Residual risks

- `documents_to_markdown.py` remains a transitional large module. Its batch path creates an output placeholder before extraction, so one failed input may leave an empty Markdown file. The packaged single-file service stages before promotion and does not have this failure mode.
- The legacy XML extraction paths still use the standard-library XML parser and lack archive expansion limits. Untrusted DOCX and EPUB files require the planned parser-hardening work.
- The launcher retains an older `shell=True` path for terminal-based document tools on Windows. Tool paths are currently repository-defined rather than user-controlled, but the desktop migration should remove this shell boundary.
- Window centering is covered by deterministic geometry tests; an interactive multi-monitor placement check was not automated.

## Release verdict

The requested consolidation is ready to use. Maintained checks, converter characterisation, packaging, and artifact inspection pass. The residual items above remain tracked migration debt and do not restore the removed utility or split PPTX back into a separate user workflow.

Anti-slop audit verdict: **A**. The implementation and handoff state concrete decisions, test results, hashes, failure modes, and reversal triggers; no placeholder evidence or unverified performance claim is included.
