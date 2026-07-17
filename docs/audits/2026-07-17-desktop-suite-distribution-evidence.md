# Desktop Suite Distribution Evidence — 2026-07-17

## Result

The repository produced a functional unsigned Windows one-folder development bundle containing
the launcher and all three GUI tools. This evidence does not authorize public redistribution.

## Automated evidence

| Check | Result |
| --- | --- |
| Locked environment | `uv sync --locked --extra suite --extra test --group desktop-build` passed |
| Test suite in generated build | 30 tests passed |
| Maintained Python UI lint | `index-app.py`, `ui_theme.py`, and `signature_gui.py` passed Ruff |
| Python compilation | launcher, theme, signer, converter, web entry point, and packager compiled |
| PyInstaller | 6.21.0, Python 3.12.10, four executables built |
| Portable artifact | `chwezi-document-suite-0.2.0-windows-x64.zip`, 71,216,820 bytes |
| Archive integrity | 1,340 entries; all four root executables present |
| Artifact SHA-256 | `8a68181677a8900dcdc484a206e9bcbd2c76fd321f6ee9edf3d2c1f83cd74d4d` |
| Manifest SHA-256 | `c581b5ca7a0181cc2b530097f3993b049d4cf3fb421d84f4923ef4c1b134cb62` |

The build's machine-readable record is generated at `release/desktop-suite-evidence.json`; the
`release/` directory is intentionally ignored by Git.

## Rendered and runtime QA

- The launcher rendered correctly in dark mode with all cards and body surfaces remapped.
- The converter rendered without clipping and used the shared light/dark design system.
- The signer rendered all placement controls, sliders, preview, and activity log after the compact
  layout adjustment.
- The organiser returned HTTP 200 on `127.0.0.1:5000`.
- The final packaged launcher, converter, and signer remained active after startup and exposed the
  expected window titles; the final packaged organiser returned HTTP 200 with a 14,669-byte page.
- Browser inspection confirmed light and dark surface changes, persisted dark mode after reload,
  and reported no console errors.
- Automated contrast checks cover primary text and accent text in both themes.

Keyboard traversal and screen-reader behaviour still require release-machine manual assessment;
this work does not claim complete WCAG conformance.

## Public-release blockers

1. The repository has no `LICENSE`, and the maintainer has not selected distribution terms.
2. Inno Setup was not installed, so an installer was not compiled.
3. Authenticode certificate and timestamp-service configuration were unavailable; the artifact is
   deliberately marked as an unsigned development build.
4. A clean-machine acceptance pass and malware scan remain required before publication.
