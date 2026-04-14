from __future__ import annotations

import json
import py_compile
from pathlib import Path

from career_common import (
    DATA_DIR,
    DOCS_DIR,
    PACKAGE_PATH,
    VALIDATION_SUMMARY_PATH,
    create_zip_bundle,
    get_logger,
    run_logged,
    write_json,
)

REQUIRED_JSON = [
    DATA_DIR / "career_master.json",
    DATA_DIR / "story_master.json",
    DATA_DIR / "career_source_index.json",
    DATA_DIR / "career_entity_timeline.json",
    DATA_DIR / "story_alias_index.json",
    Path(__file__).resolve().parents[2] / "reports" / "data" / "career_activation_summary.json",
]
REQUIRED_DOCS = [
    DOCS_DIR / "career_master_design.html",
    DOCS_DIR / "story_master_design.html",
    DOCS_DIR / "career_parsing_runbook.html",
]
REQUIRED_LOGS = [
    DATA_DIR / "build_career_master.log.txt",
    DATA_DIR / "build_story_master.log.txt",
    DATA_DIR / "activate_career_outputs.log.txt",
    DATA_DIR / "validate_career_outputs.log.txt",
]
OPTIONAL_OPPORTUNITY_FILES = [
    Path("data/opportunities/venuiti/technology_project_manager/opportunity_profile.json"),
    Path("data/opportunities/venuiti/technology_project_manager/opportunity_interview_response_bank.json"),
    Path("data/opportunities/venuiti/technology_project_manager/live_interview_config.json"),
]
CAREER_SCRIPT_DIR = Path(__file__).resolve().parent


def compile_scripts() -> list[str]:
    failures: list[str] = []
    for path in sorted(CAREER_SCRIPT_DIR.glob("*.py")):
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            failures.append(f"py_compile failed: {path} -> {exc.msg}")
    return failures


def validate_payloads() -> dict:
    failures: list[str] = []
    payloads = {}
    failures.extend(compile_scripts())
    for path in REQUIRED_JSON:
        if not path.exists():
            failures.append(f"missing required json: {path}")
            continue
        payloads[path.name] = json.loads(path.read_text(encoding="utf-8"))
    for path in REQUIRED_DOCS:
        if not path.exists():
            failures.append(f"missing required doc: {path}")
    if "career_master.json" in payloads:
        career = payloads["career_master.json"]
        for key in ["employers", "roles", "certifications", "education"]:
            if key not in career:
                failures.append(f"career_master.json missing {key}")
        for role in career.get("roles", []):
            for key in [
                "role_id", "employer_id", "dates", "location", "tools", "frameworks",
                "responsibilities", "achievements", "metrics", "stakeholders", "domains", "industries", "capability_tags",
                "customer_facing_indicators", "source_references", "evidence_confidence",
                "visibility_default", "visibility_allowed_for_target_roles", "inclusion_risk_note",
                "suppression_reason", "relevance_tags",
            ]:
                if key not in role:
                    failures.append(f"role missing {key}: {role.get('role_id', 'unknown')}")
            if not role.get("title") or not role.get("source_references"):
                failures.append(f"role missing critical content: {role.get('role_id', 'unknown')}")
    if "story_master.json" in payloads:
        story = payloads["story_master.json"]
        for item in story.get("stories", []):
            for key in [
                "story_id", "source_roles", "source_employers", "domains", "themes",
                "situation", "task", "actions", "outcomes", "tools_frameworks",
                "audience_fit", "role_fit_tags", "strength_score", "sensitivity_flags", "industries", "capability_tags", "source_references",
                "preferred_when", "avoid_when",
            ]:
                if key not in item:
                    failures.append(f"story missing {key}: {item.get('story_id', 'unknown')}")
            if not item.get("source_roles") or not item.get("actions") or not item.get("outcomes"):
                failures.append(f"story missing critical content: {item.get('story_id', 'unknown')}")
        if "career_master.json" in payloads:
            role_ids = {role["role_id"] for role in payloads["career_master.json"].get("roles", [])}
            for item in story.get("stories", []):
                missing = [role_id for role_id in item.get("source_roles", []) if role_id not in role_ids]
                if missing:
                    failures.append(f"story references missing roles: {item.get('story_id', 'unknown')} -> {missing}")
    if "story_alias_index.json" in payloads and "story_master.json" in payloads:
        story_ids = {item["story_id"] for item in payloads["story_master.json"].get("stories", [])}
        for alias in payloads["story_alias_index.json"].get("aliases", []):
            if alias.get("canonical_story_id") not in story_ids:
                failures.append(f"alias references missing canonical story: {alias.get('alias_story_id', 'unknown')}")
    if "career_activation_summary.json" in payloads:
        summary = payloads["career_activation_summary.json"]
        if not summary.get("resolved_alias_count"):
            failures.append("career activation summary missing resolved alias count")
        if not summary.get("canonical_story_ids_used"):
            failures.append("career activation summary missing canonical story ids used")
    for relative in OPTIONAL_OPPORTUNITY_FILES:
        path = Path(__file__).resolve().parents[2] / relative
        if path.exists():
            payload = json.loads(path.read_text(encoding="utf-8"))
            if path.name == "opportunity_profile.json":
                for item in payload.get("story_selection_priorities", []):
                    if "canonical_story_id" not in item:
                        failures.append(f"opportunity profile story not activated: {item.get('story_id', 'unknown')}")
                if payload.get("source_inputs_used", {}).get("requested_but_missing"):
                    failures.append("opportunity profile still lists missing inputs after activation")
            elif path.name == "opportunity_interview_response_bank.json":
                for item in payload.get("mapped_stories", []):
                    if "canonical_story_id" not in item:
                        failures.append(f"response bank story not activated: {item.get('story_id', 'unknown')}")
            elif path.name == "live_interview_config.json":
                if "priority_story_order_canonical" not in payload:
                    failures.append("live interview config missing canonical priority story order")
                if len(payload.get("priority_story_order_canonical", [])) != len(set(payload.get("priority_story_order_canonical", []))):
                    failures.append("live interview config canonical priority story order contains duplicates")
    return {"failures": failures, "payloads": payloads}


def main() -> int:
    logger = get_logger("validate_career_outputs.log.txt")

    def _run() -> None:
        result = validate_payloads()
        required_for_zip = REQUIRED_JSON + REQUIRED_DOCS + REQUIRED_LOGS + [
            Path(__file__).resolve().parents[2] / path
            for path in OPTIONAL_OPPORTUNITY_FILES
            if (Path(__file__).resolve().parents[2] / path).exists()
        ]
        required_for_zip.extend(sorted(CAREER_SCRIPT_DIR.glob("*.py")))
        if result["failures"]:
            for failure in result["failures"]:
                logger.error(failure)
        create_zip_bundle(logger, required_for_zip)
        summary = {
            "status": "passed" if not result["failures"] else "failed",
            "failure_count": len(result["failures"]),
            "failures": result["failures"],
            "package_path": str(PACKAGE_PATH),
        }
        write_json(VALIDATION_SUMMARY_PATH, summary)
        if result["failures"]:
            raise RuntimeError("career output validation failed")

    return run_logged(logger, _run)


if __name__ == "__main__":
    raise SystemExit(main())
