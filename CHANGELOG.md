# Changelog

All notable changes will be documented here. The project follows Semantic Versioning once a
public release line begins.

## Unreleased

### Added

- Transformation audit, target architecture, migration plan, roadmap, risk register, security
  model, dependency assessment, and competitive analysis.
- Initial typed `chwezi_docs` package, conversion registry and planner, capability detection,
  `DocumentSuite` facade, and Typer CLI.
- Non-destructive collision handling, staged output validation, and characterization tests.

### Changed

- Product-facing name is now Chwezi Document Suite.
- Runtime package auto-installation is disabled in transitional launchers.

### Security

- New conversion execution stages output before atomic promotion and does not overwrite input
  files by default.
- Known legacy security risks are explicitly documented; the legacy web interface is not
  production-ready.
