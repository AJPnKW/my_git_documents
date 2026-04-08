from __future__ import annotations

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / "reports" / "packages"


def main() -> int:
    if not PACKAGES.exists():
        print("packages directory missing")
        return 1

    archives = sorted(PACKAGES.glob("*.zip"))
    if not archives:
        print("no release package found")
        return 1

    latest = archives[-1]
    with zipfile.ZipFile(latest) as archive:
        names = set(archive.namelist())
        blocked = [name for name in names if name.endswith("auth_config.local.json") or name.endswith("local_project_summary.html")]
        if blocked:
          print("\n".join(blocked))
          return 1

    print("release hygiene validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
