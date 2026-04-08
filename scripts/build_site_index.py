from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"


def main() -> int:
    registry = json.loads((APP / "sites" / "_site_registry.json").read_text(encoding="utf-8"))
    payload = {"items": registry["sites"]}
    (APP / "sites" / "site_index.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print("site index built")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
