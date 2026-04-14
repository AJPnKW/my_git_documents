from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[2]
FIXED_ZIP_TIMESTAMP = (2026, 4, 9, 0, 0, 0)


def configure_logging(log_path: Path) -> logging.Logger:
    logger = logging.getLogger("company_research_package")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    return logger


def build_package(group: str, logger: logging.Logger) -> Path:
    data_dir = ROOT / "data" / "company_research" / group
    docs_dir = ROOT / "docs"
    schema_path = ROOT / "data" / "schemas" / "company_people_research.schema.json"
    downloads_dir = ROOT / ".ai_downloads"
    downloads_dir.mkdir(parents=True, exist_ok=True)

    file_list = [
        schema_path,
        data_dir / "company_people_research.json",
        data_dir / "source_index.json",
        data_dir / "people_index.json",
        data_dir / "entity_resolution.json",
        data_dir / "build_company_people_research.log.txt",
        data_dir / "render_company_research_visuals.log.txt",
        docs_dir / "company_research_design.html",
        docs_dir / "company_research_runbook.html",
        docs_dir / "venuiti_inventory.html",
        docs_dir / "venuiti_org_chart.html",
        docs_dir / "venuiti_people_graph.html",
    ]

    missing = [str(path.relative_to(ROOT)) for path in file_list if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing package inputs: {missing}")

    target = downloads_dir / f"{group}_company_research_outputs.zip"
    logger.info("Creating deterministic package at %s", target)
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in file_list:
            relative_path = path.relative_to(ROOT)
            zip_info = zipfile.ZipInfo(str(relative_path).replace("\\", "/"))
            zip_info.date_time = FIXED_ZIP_TIMESTAMP
            zip_info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(zip_info, path.read_bytes())

    manifest = {
        "group": group,
        "package_path": str(target.relative_to(ROOT)).replace("\\", "/"),
        "files": [str(path.relative_to(ROOT)).replace("\\", "/") for path in file_list],
    }
    manifest_path = data_dir / "package_company_research_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    logger.info("Package manifest written to %s", manifest_path)
    logger.info("Packaging complete.")
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Package company research outputs.")
    parser.add_argument("--group", default="venuiti", help="Group slug to package.")
    args = parser.parse_args()

    log_dir = ROOT / "data" / "company_research" / args.group
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = configure_logging(log_dir / "package_company_research.log.txt")

    try:
        build_package(args.group, logger)
    except Exception as exc:
        logger.exception("Packaging failed: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
