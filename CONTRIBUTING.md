# Contributing

Chwezi Document Suite is being migrated incrementally. Start from an issue or a narrowly scoped
change, preserve legacy behaviour with characterization tests, and avoid adding processing logic
to interface layers.

```bash
python -m pip install -e ".[dev,extract]"
python -m ruff check src tests
python -m ruff format --check src tests
python -m mypy src/chwezi_docs
python -m pytest --cov=chwezi_docs
python -m build
python -m twine check dist/*
```

Use a feature branch and focused commits. Pull requests should explain user impact, security and
privacy implications, compatibility effects, test evidence, and known limitations. Use synthetic
fixtures only; never commit confidential documents, credentials, certificates, or private keys.

Architectural changes require an ADR under `docs/architecture/decisions`. Proposed ADRs become
accepted only after review and implementation evidence.
