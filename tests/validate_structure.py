from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    required = [
        ROOT / "app" / "index.html",
        ROOT / "web" / "index.html",
        ROOT / "app" / "sites" / "_site_registry.json",
        ROOT / "app" / "sites" / "yellow_house" / "index.html",
        ROOT / "app" / "sites" / "resumes" / "index.html",
        ROOT / "app" / "shared" / "viewer" / "viewer.html",
        ROOT / "docs" / "index.html",
        ROOT / "scripts" / "build_site_index.py",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        print("\n".join(missing))
        return 1
    print("structure validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
