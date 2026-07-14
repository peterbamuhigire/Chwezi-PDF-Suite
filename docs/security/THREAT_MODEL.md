# Threat Model

## Assets and trust boundaries

Assets are original documents, generated outputs, private keys/passwords, API credentials, extracted content, job metadata and user-configured destinations. Trust boundaries exist at file/archive ingestion, workflow/config parsing, subprocess invocation, optional remote AI, local web upload/download and output promotion.

## Threats and required controls

| Threat | Current exposure | Required control and test |
|---|---|---|
| path traversal/symlink escape | AI and client paths reach filesystem operations | authorised-root resolver, symlink policy, traversal corpus |
| arbitrary overwrite/TOCTOU | direct `touch`, write and move | exclusive staging, collision policy, atomic promotion, race tests |
| ZIP/XML bombs | unbounded OOXML/EPUB reads | entry/count/size/ratio limits and safe XML parser policy |
| malicious PDF/parser exploit | files open in-process | size/page limits, maintained parsers, optional worker isolation/timeouts |
| oversized images/decompression | Pillow opens uploaded data | pixel limits, verified format, resource warning handling |
| command injection | one `shell=True` path; external converters | argument arrays, `shell=False`, executable allow-list, metacharacter tests |
| secret leakage | key in web session/response and CLI argument | keyring/env references, redacted logs, no echo/response |
| browser XSS/CSRF | untrusted `innerHTML`, state-changing routes | DOM-safe rendering, CSRF strategy, localhost policy, security tests |
| unauthorised downloads | predictable shared filenames | random job IDs, per-job roots and authorised output tokens |
| denial of service | synchronous web jobs, unbounded walks/batches | upload/job/page/time limits and bounded workers |
| CSV formula injection | future table export | escape dangerous leading characters or offer raw mode warning |
| workflow code execution | future YAML workflows | closed action schema, no Python/eval/templates with arbitrary calls |
| insecure redaction/signature claims | visual overlay only | terminology gate and backend-specific validation |
| remote data disclosure | text previews sent to AI | disabled default, consent, minimisation preview and audit event |
| plugin supply chain | future plugin concept | defer; signed/allow-listed model requires separate threat review |

## Security assumptions

The first release is single-user local software. Local documents are still untrusted inputs. Localhost does not remove browser-origin threats. Server mode, shared hosts and hostile local users require a new threat-model revision.

## Release-blocking conditions

- any path can escape its authorised root;
- input or existing output is overwritten without explicit policy;
- a secret is logged, returned to a browser or persisted in plaintext by default;
- a workflow can execute arbitrary code or shell text;
- a visual overlay is presented as secure redaction or cryptographic signing;
- a parser job has no enforceable resource/time boundary where hostile input is supported.

