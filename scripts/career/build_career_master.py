from __future__ import annotations

from career_common import (
    DATA_DIR,
    build_career_master_payload,
    build_entity_timeline,
    build_source_index,
    create_docs,
    get_logger,
    load_source_artifacts,
    run_logged,
    write_json,
)


def main() -> int:
    logger = get_logger("build_career_master.log.txt")

    def _run() -> None:
        artifacts = load_source_artifacts(logger)
        source_index = build_source_index(artifacts)
        career_master = build_career_master_payload(artifacts, logger)
        timeline = build_entity_timeline(career_master)
        write_json(DATA_DIR / "career_source_index.json", source_index)
        write_json(DATA_DIR / "career_master.json", career_master)
        write_json(DATA_DIR / "career_entity_timeline.json", timeline)
        create_docs(career_master, source_index)
        logger.info("wrote career warehouse outputs")

    return run_logged(logger, _run)


if __name__ == "__main__":
    raise SystemExit(main())
