from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[2]
FIXED_ZIP_TIMESTAMP = (2026, 4, 9, 0, 0, 0)
DEFAULT_GROUP = "venuiti"
DEFAULT_ROLE = "technology_project_manager"


def configure_logger(log_path: Path) -> logging.Logger:
    logger = logging.getLogger(f"opportunity_package::{log_path}")
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Package opportunity outputs.")
    parser.add_argument("--group", default=DEFAULT_GROUP)
    parser.add_argument("--role", default=DEFAULT_ROLE)
    args = parser.parse_args()

    data_dir = ROOT / "data" / "opportunities" / args.group / args.role
    downloads_dir = ROOT / ".ai_downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)
    log_path = data_dir / "package_opportunity.log.txt"
    data_dir.mkdir(parents=True, exist_ok=True)
    logger = configure_logger(log_path)

    files = [
        data_dir / "opportunity_profile.json",
        data_dir / "opportunity_interview_response_bank.json",
        data_dir / "live_interview_config.json",
        data_dir / "opportunity_validation_summary.json",
        data_dir / "validate_opportunity_outputs.log.txt",
        ROOT / "docs" / f"opportunity_design_{args.group}_{args.role}.html",
        ROOT / "docs" / f"opportunity_runbook_{args.group}_{args.role}.html",
        ROOT / "docs" / f"{args.group}_inventory.html",
        ROOT / "files" / "resumes" / args.group / args.role / "response_bank.html",
        ROOT / "files" / "resumes" / args.group / args.role / "org_chart.html",
        ROOT / "files" / "resumes" / args.group / args.role / "people_graph.html"
    ]

    missing = [str(path.relative_to(ROOT)).replace("\\", "/") for path in files if not path.exists()]
    if missing:
        logger.error("missing package inputs: %s", missing)
        return 1

    target = downloads_dir / f"{args.group}_{args.role}_opportunity_outputs.zip"
    logger.info("creating deterministic package at %s", target)
    with ZipFile(target, "w", compression=ZIP_DEFLATED) as archive:
        for path in files:
            zip_info = ZipInfo(str(path.relative_to(ROOT)).replace("\\", "/"))
            zip_info.date_time = FIXED_ZIP_TIMESTAMP
            zip_info.compress_type = ZIP_DEFLATED
            archive.writestr(zip_info, path.read_bytes())

    manifest = {
        "group": args.group,
        "role": args.role,
        "package_path": str(target.relative_to(ROOT)).replace("\\", "/"),
        "files": [str(path.relative_to(ROOT)).replace("\\", "/") for path in files]
    }
    manifest_path = data_dir / "package_opportunity_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    logger.info("package manifest written to %s", manifest_path)
    logger.info("packaging complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
