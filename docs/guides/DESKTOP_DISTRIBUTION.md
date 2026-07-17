# Windows Desktop Suite Distribution

## Outcome

Chwezi Document Suite is packaged as a PyInstaller one-folder multipackage bundle. The launcher
and three tool executables share one `_internal` runtime, so the launcher can open every tool
without relying on a developer Python installation:

| Executable | Source entry point | Purpose |
| --- | --- | --- |
| `ChweziDocumentSuite.exe` | `index-app.py` | suite launcher |
| `ChweziOrganizer.exe` | `web_interface.py` | localhost PDF organiser |
| `ChweziSigner.exe` | `pdf_signature.py` | visual PDF signature placement |
| `ChweziMarkdown.exe` | `documents_to_markdown.py` | document-to-Markdown converter |

Source mode still uses `sys.executable` plus each Python script. Frozen mode resolves the sibling
executables beside `ChweziDocumentSuite.exe`. This avoids the common PyInstaller failure where a
frozen launcher tries to execute a `.py` file with its own executable.

## Canonical files

- `packaging/desktop-suite.toml` is the human-maintained product manifest.
- `packaging/generated/` contains deterministic PyInstaller and Inno Setup definitions plus the
  manifest hash.
- `scripts/build-desktop-suite.ps1` is the generated local/CI build command.
- `.github/workflows/windows-desktop-suite.yml` verifies the bundle on Windows.
- `uv.lock` fixes the Python dependency graph.

Generated files must be regenerated after any manifest change. The build script compares the
manifest hash and fails rather than building stale packaging definitions.

## Workstation preparation

Use Python 3.12 on Windows and install `uv`. For public installers, also install Inno Setup 6 and a
Windows SDK that provides `signtool.exe`.

```powershell
uv sync --locked --extra suite --extra test --group desktop-build
```

The applications never install dependencies while running.

## Diagnose and generate

The packaging generator lives in Peter's canonical software-engineering skill engine:

```powershell
$Packager = 'C:\Users\Peter\.claude\skills\skills\languages\python-modern-standards\scripts\desktop_suite_packager.py'
python $Packager doctor --config packaging\desktop-suite.toml
python $Packager generate --config packaging\desktop-suite.toml
```

`doctor` validates entry points, bundled data, notices, dependency locking, unsafe subprocess
patterns, and release prerequisites. For this repository it intentionally blocks an external
release until a maintainer adds the selected `LICENSE`. It also reports missing Inno Setup as an
installer warning.

## Build and verify

For local visual and runtime testing:

```powershell
.\scripts\build-desktop-suite.ps1 -UnsignedDevelopmentBuild -SkipInstaller
```

This command performs a locked sync, runs the test suite, builds all executables, verifies required
bundle paths, creates the portable ZIP, and records artifact size and SHA-256 in
`release/desktop-suite-evidence.json`. Extract the ZIP as one folder; do not move an individual EXE
away from `_internal` or the other executables.

Before release, test on a clean supported Windows machine:

1. Start `ChweziDocumentSuite.exe` and launch all three cards.
2. Switch light/dark mode and restart each GUI to confirm preference persistence.
3. Convert representative PDF, EPUB, DOCX, DOC, and PPTX files.
4. Preview and place a signature on a disposable PDF.
5. Start the organiser, confirm it binds only to `127.0.0.1`, and exercise file selection and a
   dry-run workflow.
6. Scan the artifact and review `THIRD_PARTY_NOTICES.md` against the locked dependency set.

## Signed public release

Do not use `-UnsignedDevelopmentBuild` for distribution. First add the maintainer-approved licence,
install Inno Setup, make the signing certificate available to the current user, then set:

```powershell
$env:WINDOWS_CERT_SHA1 = '<certificate thumbprint>'
$env:WINDOWS_TIMESTAMP_URL = 'https://<trusted-rfc3161-timestamp-service>'
.\scripts\build-desktop-suite.ps1
```

The script signs and verifies the executable artifacts, compiles the Inno Setup installer, and
includes hashes in the evidence record. Signing secrets and certificate files must never enter the
repository.

## Reuse in another Python tools project

From the other repository, initialize a manifest with the same engine script:

```powershell
python $Packager init --config packaging\desktop-suite.toml
```

Edit product identity, launcher, applications, data paths, dependency sync arguments, quality
commands, and release policy. A custom launcher should use `[product].launcher_script`; otherwise
the generator creates a minimal frozen-safe launcher. Then run `doctor`, `generate`, and the
generated PowerShell build. Commit the manifest, generated definitions, workflow, and dependency
lock—not `build/`, `dist/`, `release/`, `.venv/`, certificates, or signing secrets.

## Current release status

The 2026-07-17 verification produced a working unsigned portable development ZIP. Public
redistribution is not approved because the repository licence is unresolved, Inno Setup is not
installed on the validation workstation, and Authenticode credentials were not configured. See
the corresponding [distribution evidence](../audits/2026-07-17-desktop-suite-distribution-evidence.md).
