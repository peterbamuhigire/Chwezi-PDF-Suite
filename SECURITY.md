# Security Policy

Chwezi Document Suite is pre-alpha software. It processes untrusted, structurally complex
files and should not yet be deployed as an internet-facing service.

## Reporting a vulnerability

Do not open a public issue containing exploit details, secrets, private documents, or personal
data. Use GitHub's private vulnerability reporting feature for this repository when available.
If it is unavailable, contact the repository owner privately through the contact method on the
owner's GitHub profile and request a secure reporting channel.

Include the affected version or commit, operating system, reproduction steps using a synthetic
fixture, expected impact, and any proposed mitigation. Do not attach confidential source
documents.

## Supported versions

No production-supported release exists yet. Security fixes currently target the `main` branch
and the active release-candidate branch. This policy will gain a version support table before
the first stable release.

## Current deployment boundary

- Use local processing on trusted workstations only.
- Do not expose the legacy Flask interface beyond localhost.
- Do not process hostile files outside an isolated environment.
- Do not enable external AI providers without informed consent for document transmission.
- Keep originals; generated output is non-destructive by default in the new core.

The detailed threat analysis and deployment controls are in
[`docs/security/THREAT_MODEL.md`](docs/security/THREAT_MODEL.md) and
[`docs/security/SECURE_DEPLOYMENT.md`](docs/security/SECURE_DEPLOYMENT.md).
