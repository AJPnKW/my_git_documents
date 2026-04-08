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
    posting = APP / "sites" / "resumes" / "companies" / "venuiti" / "postings" / "technology_project_manager"
    for name in ["job_posting.html", "resume.html", "notes.html", "interview_questions.html", "posting.json"]:
        if not (posting / name).exists():
            failures.append(f"missing {name}")
    if failures:
      print("\n".join(failures))
      return 1
    print("manifest validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
