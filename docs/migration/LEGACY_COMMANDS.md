# Legacy Command Migration

| Legacy script | New command | Compatibility status | Planned removal |
|---|---|---|---|
| `pdf_to_epub.py` | `chwezi convert FILE --to markdown` | retained; name is misleading | after two parity releases |
| `pptx_to_epub.py` | `chwezi convert DECK.pptx --to markdown` | retained; name is misleading | after two parity releases |
| `organize_batch.py` | `chwezi organise PATH` | retained; migration not implemented | after P1 parity |
| `pdf_signature.py` | `chwezi sign FILE --signature IMAGE` | retained; visual placement only | after P1 parity |
| `sign_setup.py` | `chwezi sign` or desktop Sign tool | retained during transition | after P1 parity |
| `watch_organizer.py` | `chwezi watch PATH --workflow NAME` | retained; not recoverable | after durable-watch parity |
| `watch_setup.py` | `chwezi watch` | retained during transition | after durable-watch parity |
| `web_interface.py` | `chwezi web` | development-only, security-blocked for network use | after local FastAPI replacement |
| `index-app.py` | `chwezi desktop` | retained during desktop transition | after PySide6 parity |
| `fetch-categories.py` | `chwezi organise categories import` | retained utility | after importer exists |
| `diagnose.py` | `chwezi diagnostics` | retained utility | after diagnostic parity |

Removal dates are milestone-based because no release cadence has been approved. Deprecation warnings will begin only when the replacement command is implemented.

