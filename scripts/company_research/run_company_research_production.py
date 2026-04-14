from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def run_step(name: str, command: list[str], log_lines: list[str]) -> None:
    started = datetime.now(timezone.utc).isoformat()
    log_lines.append(f"[{started}] START {name}: {' '.join(command)}")
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if result.stdout:
        log_lines.append(result.stdout.rstrip())
    if result.stderr:
        log_lines.append(result.stderr.rstrip())
    ended = datetime.now(timezone.utc).isoformat()
    log_lines.append(f"[{ended}] END {name}: exit_code={result.returncode}")
    if result.returncode != 0:
        raise RuntimeError(f"{name} failed with exit code {result.returncode}")


def write_run_summary(group: str, status: str, steps: list[str], error: str | None = None) -> Path:
    data_dir = ROOT / "data" / "company_research" / group
    payload_path = data_dir / "company_people_research.json"
    payload = json.loads(payload_path.read_text(encoding="utf-8")) if payload_path.exists() else {}
    summary = {
        "group": group,
        "status": status,
        "completed_at_utc": datetime.now(timezone.utc).isoformat(),
        "steps": steps,
        "error": error,
        "outputs": {
            "research_json": str(payload_path.relative_to(ROOT)).replace("\\", "/"),
            "package": f".ai_downloads/{group}_company_research_outputs.zip",
            "org_chart": "docs/venuiti_org_chart.html",
            "people_graph": "docs/venuiti_people_graph.html",
            "validation_report": f"data/company_research/{group}/validate_company_research_outputs_report.json",
        },
        "counts": {
            "companies": len(payload.get("companies", [])),
            "people": len(payload.get("people", [])),
            "org_nodes": len(payload.get("org_structure_inferred", {}).get("nodes", [])),
            "org_relationships": len(payload.get("org_structure_inferred", {}).get("relationships", [])),
            "people_graph_nodes": len(payload.get("people_graph_inferred", {}).get("nodes", [])),
            "people_graph_relationships": len(payload.get("people_graph_inferred", {}).get("relationships", [])),
        },
    }
    summary_path = data_dir / "run_company_research_production_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build, validate, render, and package company research outputs.")
    parser.add_argument("--group", default="venuiti", help="Group slug to process.")
    parser.add_argument("--skip-repo-validation", action="store_true", help="Skip the full repository validation suite.")
    args = parser.parse_args()

    data_dir = ROOT / "data" / "company_research" / args.group
    data_dir.mkdir(parents=True, exist_ok=True)
    log_path = data_dir / "run_company_research_production.log.txt"
    log_lines: list[str] = []
    steps: list[str] = []

    step_commands = [
        ("build", [sys.executable, "scripts/company_research/build_company_people_research.py", "--group", args.group]),
        ("render_visuals", [sys.executable, "scripts/company_research/render_company_research_visuals.py", "--group", args.group]),
        ("validate_outputs", [sys.executable, "scripts/company_research/validate_company_research_outputs.py", "--group", args.group]),
        ("package", [sys.executable, "scripts/company_research/package_company_research.py", "--group", args.group]),
        ("validate_package", [sys.executable, "scripts/company_research/validate_company_research_outputs.py", "--group", args.group, "--require-package"]),
    ]
    if not args.skip_repo_validation:
        step_commands.append(("repo_validation", [sys.executable, "tests/run_all.py"]))

    try:
        for name, command in step_commands:
            run_step(name, command, log_lines)
            steps.append(name)
        summary_path = write_run_summary(args.group, "passed", steps)
        log_lines.append(f"Production run summary: {summary_path}")
        print(f"company research production run passed; summary written to {summary_path}")
        return 0
    except Exception as exc:
        summary_path = write_run_summary(args.group, "failed", steps, str(exc))
        log_lines.append(f"FAILED: {exc}")
        log_lines.append(f"Production run summary: {summary_path}")
        print(f"company research production run failed; summary written to {summary_path}")
        return 1
    finally:
        log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
