# Chwezi icon assets

These SVGs were supplied by the project owner from the local collection
`Chwezi-Document-Suite-Icons-2026-07-17`. The original files remain outside the repository in
the owner's Downloads folder.

The project copies repair missing `chweziGradient` definitions found during import. The source
drawings are otherwise retained. `scripts/build_icon_assets.py` validates paint references and
generates theme-specific PNGs plus multi-size Windows ICO files.

## Regenerate desktop assets

```powershell
python -X utf8 scripts\build_icon_assets.py
```

The renderer uses an installed Chrome or Microsoft Edge browser. Pillow writes the ICO
containers. Neither dependency is required at application runtime beyond the Pillow dependency
already included in the packaged desktop suite.

## Licence record

The repository does not contain the subscription provider's receipt or licence text. Retain the
commercial licence evidence with release records before distributing an installer or portable
archive outside the organisation.
