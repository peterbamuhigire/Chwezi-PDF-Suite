# Secure File Handling

## Input policy

Detect type from extension plus signature where possible. Reject unsupported/encrypted inputs with actionable errors. Enforce configured byte, page, image-pixel, archive-entry and expanded-size limits before expensive processing.

## Output policy

1. Resolve source and authorised output root.
2. Select collision policy: fail, skip, rename or explicit overwrite.
3. Create a job-specific staging directory under a trusted root.
4. Write output without touching the final path.
5. Validate existence, size, signature and parser reopen where supported.
6. Atomically promote on the same filesystem; document fallback semantics otherwise.
7. Clean staging on success, failure and cancellation.

Organisation moves also write an undo manifest before the first mutation. A batch failure does not remove successful outputs unless atomic batch mode was explicitly selected.

## Archive policy

Inspect central-directory metadata before reading OOXML/EPUB members. Reject absolute paths, drive prefixes, `..` traversal, excessive entries, expanded bytes and suspicious compression ratios. Read only declared members and cap actual streamed bytes because archive metadata can lie.

## Logging policy

Log job IDs and sanitised references, not document text, passwords, API keys, private-key material or full paths by default. Debug logs require an explicit privacy warning and still redact secrets.

