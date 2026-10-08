import json
import os
from datetime import datetime
from pathlib import Path

ebooks_root = Path(".").resolve()

categories = []
for root, _dirs, files in os.walk(ebooks_root):
    root_path = Path(root)
    if root_path == ebooks_root:
        continue
    rel = root_path.relative_to(ebooks_root)
    pdf_count = sum(1 for f in files if f.lower().endswith(".pdf"))
    parts = rel.parts
    categories.append({
        "path": "/".join(parts),
        "depth": len(parts),
        "count": pdf_count
    })

payload = {
    "generated_at": datetime.now().isoformat(),
    "ebooks_root": str(ebooks_root),
    "category_count": len(categories),
    "categories": sorted(categories, key=lambda x: x["path"])
}

out_path = ebooks_root / "category_template.json"
out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Template saved to {out_path}")