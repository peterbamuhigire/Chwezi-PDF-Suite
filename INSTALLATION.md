# Installation

Chwezi Document Suite currently supports source installations for development and evaluation.
Published packages and desktop installers do not exist yet.

## Requirements

- Python 3.11 or 3.12 (3.12 is the primary target)
- `pip` and a virtual environment
- Optional LibreOffice for legacy DOC conversion

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[extract]"
chwezi capabilities
```

On macOS or Linux, activate with `source .venv/bin/activate`. Install development tooling with
`python -m pip install -e ".[dev,extract]"`.

Feature extras are `desktop`, `web`, `ocr`, `office`, `ai`, `sign`, `watch`, `extract`, `test`,
and `dev`. The `all` extra is for evaluation, not a recommendation for minimal deployments.
System dependencies are documented in [`docs/reference/DEPENDENCIES.md`](docs/reference/DEPENDENCIES.md).

Applications report missing capabilities; they do not install packages during execution.
