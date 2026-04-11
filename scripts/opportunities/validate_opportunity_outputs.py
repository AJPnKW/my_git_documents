from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXED_GROUP = "venuiti"
FIXED_ROLE = "technology_project_manager"


def configure_logger(log_path: Path) -> logging.Logger:
    logger = logging.getLogger(f"opportunity_validate::{log_path}")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


def validate_json_payload(path: Path, required_keys: list[str], logger: logging.Logger) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"missing required file: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    missing = [key for key in required_keys if key not in payload]
    if missing:
        raise KeyError(f"{path.name} missing keys: {missing}")
    logger.info("validated json payload: %s", path.relative_to(ROOT))
    return payload


def validate_html_doc(path: Path, logger: logging.Logger) -> None:
    if not path.exists():
        raise FileNotFoundError(f"missing required doc: {path}")
    text = path.read_text(encoding="utf-8")
    if "<!DOCTYPE html>" not in text or "<html" not in text.lower():
        raise ValueError(f"invalid html doc: {path}")
    logger.info("validated html doc: %s", path.relative_to(ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate opportunity outputs.")
    parser.add_argument("--group", default=FIXED_GROUP)
    parser.add_argument("--role", default=FIXED_ROLE)
    args = parser.parse_args()

    data_dir = ROOT / "data" / "opportunities" / args.group / args.role
    docs_dir = ROOT / "docs"
    role_files_dir = ROOT / "files" / "resumes" / args.group / args.role
    log_path = data_dir / "validate_opportunity_outputs.log.txt"
    data_dir.mkdir(parents=True, exist_ok=True)
    logger = configure_logger(log_path)

    try:
        profile = validate_json_payload(
            data_dir / "opportunity_profile.json",
            [
                "opportunity_identity",
                "role_summary",
                "must_haves",
                "nice_to_haves",
                "hidden_inferred_priorities",
                "company_context_overlays",
                "interviewer_context_overlays",
                "story_selection_priorities",
                "risk_areas_gaps_sensitivities",
                "answer_tone_guidance",
                "validation",
                "build_log",
            ],
            logger,
        )
        response_bank = validate_json_payload(
            data_dir / "opportunity_interview_response_bank.json",
            [
                "likely_question_bank",
                "question_categories",
                "mapped_stories",
                "response_variants",
                "watchouts",
                "continuity_rules",
                "anti_overexplaining_guidance",
                "examples_to_prioritize",
                "examples_to_avoid",
                "fallback_answer_patterns_for_uncertainty",
                "validation",
                "build_log",
            ],
            logger,
        )
        validate_json_payload(
            data_dir / "live_interview_config.json",
            [
                "opportunity_id",
                "opening_positioning",
                "priority_story_order",
                "response_controls",
                "logging",
                "validation",
                "build_log",
            ],
            logger,
        )

        for doc_name in [
            f"opportunity_design_{args.group}_{args.role}.html",
            f"opportunity_runbook_{args.group}_{args.role}.html",
        ]:
            validate_html_doc(docs_dir / doc_name, logger)

        for name in [
            "posting.html",
            "resume.html",
            "posting_analysis.html",
            "interview_prep.html",
            "interview_notes.html",
            "interview_questions.html",
            "response_bank.html",
            "org_chart.html",
            "people_graph.html",
        ]:
            path = role_files_dir / name
            if not path.exists():
                raise FileNotFoundError(f"missing role workspace artifact: {path}")
            logger.info("validated role artifact: %s", path.relative_to(ROOT))

        source_inputs = profile.get("source_inputs_used", {})
        missing = source_inputs.get("requested_but_missing", [])
        if missing:
            raise ValueError(f"opportunity profile still reports missing required inputs: {missing}")

        if not response_bank.get("response_variants"):
            raise ValueError("response bank has no response_variants")

        summary = {
            "status": "passed",
            "group": args.group,
            "role": args.role,
            "validated_files": [
                str((data_dir / "opportunity_profile.json").relative_to(ROOT)).replace("\\", "/"),
                str((data_dir / "opportunity_interview_response_bank.json").relative_to(ROOT)).replace("\\", "/"),
                str((data_dir / "live_interview_config.json").relative_to(ROOT)).replace("\\", "/"),
                str((docs_dir / f"opportunity_design_{args.group}_{args.role}.html").relative_to(ROOT)).replace("\\", "/"),
                str((docs_dir / f"opportunity_runbook_{args.group}_{args.role}.html").relative_to(ROOT)).replace("\\", "/")
            ]
        }
        (data_dir / "opportunity_validation_summary.json").write_text(
            json.dumps(summary, indent=2) + "\n",
            encoding="utf-8",
        )
        logger.info("opportunity validation passed")
        return 0
    except Exception as exc:
        logger.exception("opportunity validation failed: %s", exc)
        summary = {
            "status": "failed",
            "group": args.group,
            "role": args.role,
            "error": str(exc)
        }
        (data_dir / "opportunity_validation_summary.json").write_text(
            json.dumps(summary, indent=2) + "\n",
            encoding="utf-8",
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
