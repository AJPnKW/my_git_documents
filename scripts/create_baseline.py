from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKUPS = ROOT / "backups"
REPORTS = ROOT / "reports" / "data"


def main() -> int:
    stamp = datetime.now().strftime("%Y%m%d__%H%M%S")
    target = BACKUPS / f"baseline__{stamp}"
    target.mkdir(parents=True, exist_ok=True)

    for item in ROOT.iterdir():
        if item.name in {".git", "__pycache__", "backups"}:
            continue
        destination = target / item.name
        if item.is_dir():
            shutil.copytree(item, destination, dirs_exist_ok=True)
        else:
            shutil.copy2(item, destination)

    metadata = {
        "baseline_id": target.name,
        "created_at": datetime.now().isoformat(),
        "path": str(target.relative_to(ROOT)).replace("\\", "/")
    }
    (target / "baseline_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
