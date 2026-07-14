# Risk Register

Scoring: probability 1–5 multiplied by impact 1–5. Scores 1–4 low, 5–9 medium, 10–15 high, 16–25 critical. Scores are current engineering judgement from the audited code and must be recalibrated with test and user evidence.

| ID | Cause, event and impact | P | I | Score | Response | Owner | Trigger / evidence |
|---|---|---:|---:|---:|---|---|---|
| R-001 | Unvalidated AI category or filename escapes the destination root, causing arbitrary moves or overwrite | 4 | 5 | 20 | avoid: safe path templates and containment checks before organisation ships | core maintainer | traversal security test fails |
| R-002 | Web debug/network exposure and client-side secrets disclose files or credentials | 4 | 5 | 20 | block network use; replace adapter and secret storage | web owner | any non-local bind or key in response/cookie |
| R-003 | No licence plus incompatible dependency obligations prevents lawful distribution | 4 | 5 | 20 | decide project licence; complete dependency/asset notice review | maintainer | release packaging review incomplete |
| R-004 | Output overwrite or direct move destroys user data | 4 | 5 | 20 | stage, validate, collision policy and undo manifest | filesystem owner | destructive regression test fails |
| R-005 | ZIP/XML bombs exhaust memory/disk during OOXML/EPUB extraction | 3 | 5 | 15 | archive limits and controlled fixtures | security owner | limit bypass or unbounded read found |
| R-006 | Conversion claims exceed tested fidelity and damage trust | 4 | 4 | 16 | capability matrix, warnings and golden corpus | conversion owner | unsupported claim in docs/UI |
| R-007 | Broad refactor breaks valuable Markdown/signature behaviour | 4 | 4 | 16 | strangler migration and characterisation tests | tech lead | parity fixture changes without approval |
| R-008 | Heavy optional packages make core install fragile | 4 | 3 | 12 | extras and capability degradation | packaging owner | clean core install downloads GUI/OCR/cloud stack |
| R-009 | Cross-platform external tools behave differently | 4 | 4 | 16 | adapters, version probes and three-OS CI | release owner | matrix failure or undocumented limitation |
| R-010 | Large files exhaust memory or temporary space | 3 | 5 | 15 | configurable limits, estimates, streaming and benchmarks | performance owner | 1000-page/500 MB test exceeds budget |
| R-011 | Remote AI receives sensitive content without informed consent | 3 | 5 | 15 | disabled default, minimisation preview and audit trail | privacy owner | content leaves local boundary without explicit setting |
| R-012 | Digital-signature or redaction wording creates false assurance | 3 | 5 | 15 | strict terminology and specialist validation | product/security owner | visual stamp labelled digital signature |
| R-013 | Worker crash leaves jobs or temporary data orphaned | 3 | 4 | 12 | durable states, startup recovery and retention cleanup | job owner | interrupted-job recovery test fails |
| R-014 | Maintainer capacity is diluted by unrelated utilities and P2 work | 4 | 3 | 12 | scope boundaries and milestone gates | product owner | P2 work starts before P0 exit |
| R-015 | Dependency API/security changes break unpinned installs | 4 | 4 | 16 | lock file, Dependabot, audit and compatibility CI | packaging owner | resolver drift or advisory |
| R-016 | Test corpus contains confidential or encumbered documents | 2 | 5 | 10 | synthetic/public-domain fixtures with provenance manifest | test owner | fixture lacks provenance |

## Monitoring

Review at each milestone and whenever a converter, external executable, remote provider, web exposure or file-mutation policy changes. Risk acceptance requires the maintainer's explicit record; this document does not accept residual risk.

