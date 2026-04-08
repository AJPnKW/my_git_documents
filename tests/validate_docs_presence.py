from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    required = [
        ROOT / "docs" / "index.html",
        ROOT / "docs" / "project_scope.html",
        ROOT / "docs" / "architecture.html",
        ROOT / "docs" / "configuration.html",
        ROOT / "docs" / "security_model.html",
        ROOT / "docs" / "content_model.html",
        ROOT / "docs" / "user_workflows.html",
        ROOT / "docs" / "admin_guide.html",
        ROOT / "docs" / "qa_validation.html",
        ROOT / "docs" / "change_log.html",
        ROOT / "docs" / "codex_delivery_plan.html",
        ROOT / "docs" / "operations_dashboard.html",
        ROOT / "docs" / "baselines" / "index.html",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        print("\n".join(missing))
        return 1
    print("docs presence validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
