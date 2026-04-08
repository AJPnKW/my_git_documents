from __future__ import annotations

import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ROOT / "reports" / "packages"


def main() -> int:
    stamp = datetime.now().strftime("%Y%m%d__%H%M%S")
    target = PACKAGES / f"my_git_documents__package__{stamp}.zip"
    target.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in ROOT.rglob("*"):
            if (
                ".git" in path.parts
                or "backups" in path.parts
                or "__pycache__" in path.parts
                or "packages" in path.parts
                or path.name == "auth_config.local.json"
                or path.name == "local_project_summary.html"
            ):
                continue
            if path.is_file():
                archive.write(path, path.relative_to(ROOT))

    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
