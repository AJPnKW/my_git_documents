from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"


def main() -> int:
    failures = []
    for path in [
        APP / "sites" / "yellow_house" / "manifest.json",
        APP / "sites" / "resumes" / "manifest.json",
    ]:
        data = json.loads(path.read_text(encoding="utf-8"))
        for field in ["site_key", "title", "access_mode"]:
            if field not in data:
                failures.append(f"{path}: missing {field}")
    posting = ROOT / "files" / "resumes" / "venuiti" / "technology_project_manager"
    for name in ["posting.html", "resume.html", "posting_analysis.html", "interview_prep.html", "interview_notes.html"]:
        if not (posting / name).exists():
            failures.append(f"missing {name}")
    if not (ROOT / "files" / "single_page" / "yellow_house" / "source.html").exists():
        failures.append("missing files/single_page/yellow_house/source.html")
    for name in ["yellow_house.json", "resumes.json"]:
        if not (APP / "data" / "workspaces" / name).exists():
            failures.append(f"missing app/data/workspaces/{name}")
    if failures:
      print("\n".join(failures))
      return 1
    print("manifest validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
