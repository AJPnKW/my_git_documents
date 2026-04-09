from __future__ import annotations

import json
import os
import re
import shutil
import stat
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
WEB = ROOT / "web"
FILES = ROOT / "files"

SITE_PREFIX = "../../../"
ROLE_ORDER = [
    ("posting", "Job Posting", True),
    ("resume", "Resume", True),
    ("posting_analysis", "Posting Analysis", False),
    ("interview_prep", "Interview Prep", False),
    ("interview_notes", "Interview Notes", False),
]
DOC_EXTENSIONS = {".html", ".pdf", ".docx"}


def titleize(value: str) -> str:
    words = re.split(r"[_\-]+", value.strip())
    return " ".join(word.upper() if word.isupper() else word.capitalize() for word in words if word)


def html_title(path: Path) -> str | None:
    if path.suffix.lower() != ".html":
        return None
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"<title>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(1)).strip()


def relative_href(path: Path) -> str:
    return SITE_PREFIX + path.relative_to(ROOT).as_posix()


def single_page_workspace(topic_dir: Path) -> dict:
    docs = sorted(
        path for path in topic_dir.iterdir()
        if path.is_file() and path.suffix.lower() in DOC_EXTENSIONS
    )
    items = []
    for index, path in enumerate(docs):
        label = html_title(path) or titleize(path.stem)
        parts = [part.strip() for part in re.split(r"\s+[—-]\s+", label) if part.strip()]
        if parts:
            label = parts[-1]
        if "rental investor analysis" in label.lower():
            label = "Rental Investor Analysis"
        items.append(
            {
                "id": f"{topic_dir.name}-doc-{index + 1}",
                "type": "file",
                "label": label,
                "description": "",
                "href": relative_href(path),
                "selected": index == 0,
            }
        )

    return {
        "siteKey": topic_dir.name,
        "siteTitle": "",
        "siteSummary": "",
        "hideSidebarHeader": True,
        "showNotes": False,
        "showToolbarStatus": False,
        "showPanelHeader": False,
        "defaultMode": "single",
        "noteStorageKey": f"mgd:notes:{topic_dir.name}",
        "notePlaceholder": "",
        "tree": [
            {
                "id": f"{topic_dir.name}-files",
                "type": "folder",
                "label": "Files",
                "open": True,
                "children": items,
            }
        ],
    }


def resumes_workspace(resumes_root: Path) -> dict:
    tree = []
    first_posting = True
    for company_dir in sorted(path for path in resumes_root.iterdir() if path.is_dir()):
        company_children = []
        for posting_dir in sorted(path for path in company_dir.iterdir() if path.is_dir()):
            file_children = []
            for stem, label, default_selected in ROLE_ORDER:
                candidates = sorted(posting_dir.glob(f"{stem}.*"))
                if candidates:
                    path = candidates[0]
                    file_children.append(
                        {
                            "id": f"{company_dir.name}-{posting_dir.name}-{stem}",
                            "type": "file",
                            "label": label,
                            "description": "",
                            "href": relative_href(path),
                            "selected": first_posting and default_selected,
                        }
                    )
                else:
                    file_children.append(
                        {
                            "id": f"{company_dir.name}-{posting_dir.name}-{stem}",
                            "type": "file",
                            "label": f"{label} (to add)",
                            "description": "",
                            "href": "",
                            "selected": False,
                            "disabled": True,
                            "placeholder": True,
                        }
                    )
            company_children.append(
                {
                    "id": f"{company_dir.name}-{posting_dir.name}",
                    "type": "folder",
                    "label": titleize(posting_dir.name),
                    "open": first_posting,
                    "children": file_children,
                }
            )
            first_posting = False

        tree.append(
            {
                "id": company_dir.name,
                "type": "folder",
                "label": titleize(company_dir.name),
                "open": True,
                "children": company_children,
            }
        )

    return {
        "siteKey": "resumes",
        "siteTitle": "",
        "siteSummary": "",
        "hideSidebarHeader": True,
        "showNotes": True,
        "showToolbarStatus": False,
        "showPanelHeader": False,
        "defaultMode": "split",
        "noteStorageKey": "mgd:notes:resumes",
        "notePlaceholder": "Write the interview question, your answer notes, follow-up tasks, or any general notes here.",
        "tree": tree,
    }


def build_workspaces() -> dict[str, dict]:
    workspaces = {}
    single_root = FILES / "single_page"
    if single_root.exists():
        for topic_dir in sorted(path for path in single_root.iterdir() if path.is_dir()):
            workspaces[topic_dir.name] = single_page_workspace(topic_dir)

    resumes_root = FILES / "resumes"
    if resumes_root.exists():
        workspaces["resumes"] = resumes_workspace(resumes_root)

    return workspaces


def write_workspace_json(target_root: Path, workspaces: dict[str, dict]) -> None:
    data_root = target_root / "data" / "workspaces"
    data_root.mkdir(parents=True, exist_ok=True)
    for name, payload in workspaces.items():
        (data_root / f"{name}.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def on_rm_error(func, path, exc_info):
    target = Path(path)
    if target.is_dir():
        shutil.rmtree(target, onerror=on_rm_error)
        return
    os.chmod(path, stat.S_IWRITE)
    func(path)


def sync_web_from_app() -> None:
    temp_parent = Path(tempfile.mkdtemp(prefix="mgd_web_build_", dir=ROOT))
    temp_web = temp_parent / "web"
    shutil.copytree(
        APP,
        temp_web,
        ignore=shutil.ignore_patterns("auth_config.local.json"),
    )
    old_web = None
    if WEB.exists():
        old_web = ROOT / f"web__old__{next(tempfile._get_candidate_names())}"
        WEB.replace(old_web)
    temp_web.replace(WEB)
    shutil.rmtree(temp_parent, onerror=on_rm_error)
    if old_web and old_web.exists():
        try:
            shutil.rmtree(old_web, onerror=on_rm_error)
        except Exception:
            pass


def main() -> int:
    registry = json.loads((APP / "sites" / "_site_registry.json").read_text(encoding="utf-8"))
    payload = {"items": registry["sites"]}
    (APP / "sites" / "site_index.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    workspaces = build_workspaces()
    write_workspace_json(APP, workspaces)
    sync_web_from_app()

    print("site index built")
    print("workspace data built")
    print("web mirror generated from app")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
