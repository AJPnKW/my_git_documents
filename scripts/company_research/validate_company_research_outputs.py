from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = ROOT / "data" / "company_research"
DOCS_DIR = ROOT / "docs"
SCHEMA_PATH = ROOT / "data" / "schemas" / "company_people_research.schema.json"
DOWNLOADS_DIR = ROOT / ".ai_downloads"

ALLOWED_ORG_NODE_TYPES = {"company", "brand", "function", "department", "team"}
ALLOWED_ORG_RELATIONSHIPS = {"belongs_to", "supports", "operates_within", "cross_function"}
ALLOWED_PEOPLE_RELATIONSHIPS = {
    "works_with",
    "associated_with",
    "likely_same_team",
    "cross_entity",
}
REQUIRED_DOCS = [
    "company_research_design.html",
    "company_research_runbook.html",
    "venuiti_org_chart.html",
    "venuiti_people_graph.html",
]
REQUIRED_DATA_FILES = [
    "company_people_research.json",
    "source_index.json",
    "people_index.json",
    "entity_resolution.json",
    "build_company_people_research.log.txt",
    "render_company_research_visuals.log.txt",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def add_error(errors: list[str], message: str) -> None:
    errors.append(message)


def require_file(errors: list[str], path: Path) -> None:
    if not path.exists():
        add_error(errors, f"Missing required file: {path.relative_to(ROOT)}")


def validate_schema(errors: list[str], payload: dict[str, Any]) -> None:
    schema = load_json(SCHEMA_PATH)
    try:
        jsonschema.validate(payload, schema)
    except jsonschema.ValidationError as exc:
        add_error(errors, f"Schema validation failed: {exc.message}")


def validate_org_graph(errors: list[str], payload: dict[str, Any]) -> None:
    graph = payload.get("org_structure_inferred", {})
    nodes = graph.get("nodes", [])
    relationships = graph.get("relationships", [])
    node_ids = [node.get("id") for node in nodes]
    unique_node_ids = {node_id for node_id in node_ids if node_id}

    if len(unique_node_ids) != len(node_ids):
        add_error(errors, "org_structure_inferred.nodes contains duplicate or empty ids.")

    for node in nodes:
        node_id = node.get("id", "<missing>")
        node_type = node.get("type")
        parent_id = node.get("parent_id")
        if node_type not in ALLOWED_ORG_NODE_TYPES:
            add_error(errors, f"Org node {node_id} has unsupported type: {node_type}")
        if parent_id is not None and parent_id not in unique_node_ids:
            add_error(errors, f"Org node {node_id} references missing parent_id: {parent_id}")
        if not node.get("evidence"):
            add_error(errors, f"Org node {node_id} has no evidence.")

    for rel in relationships:
        from_id = rel.get("from_id")
        to_id = rel.get("to_id")
        rel_type = rel.get("relationship_type")
        if from_id not in unique_node_ids:
            add_error(errors, f"Org relationship references missing from_id: {from_id}")
        if to_id not in unique_node_ids:
            add_error(errors, f"Org relationship references missing to_id: {to_id}")
        if rel_type not in ALLOWED_ORG_RELATIONSHIPS:
            add_error(errors, f"Org relationship {from_id}->{to_id} has unsupported type: {rel_type}")
        if not rel.get("evidence"):
            add_error(errors, f"Org relationship {from_id}->{to_id} has no evidence.")


def validate_people_graph(errors: list[str], payload: dict[str, Any]) -> None:
    people = payload.get("people", [])
    org_nodes = payload.get("org_structure_inferred", {}).get("nodes", [])
    graph = payload.get("people_graph_inferred", {})
    graph_nodes = graph.get("nodes", [])
    relationships = graph.get("relationships", [])

    payload_people_ids = {person.get("person_id") for person in people}
    graph_people_ids = [node.get("person_id") for node in graph_nodes]
    unique_graph_people_ids = {person_id for person_id in graph_people_ids if person_id}
    org_node_ids = {node.get("id") for node in org_nodes}

    if len(unique_graph_people_ids) != len(graph_people_ids):
        add_error(errors, "people_graph_inferred.nodes contains duplicate or empty person_id values.")

    for node in graph_nodes:
        person_id = node.get("person_id", "<missing>")
        if person_id not in payload_people_ids:
            add_error(errors, f"People graph node references missing person: {person_id}")
        for entity_id in node.get("associated_entities", []):
            if entity_id not in org_node_ids:
                add_error(errors, f"People graph node {person_id} references missing entity: {entity_id}")

    for rel in relationships:
        from_person_id = rel.get("from_person_id")
        to_person_id = rel.get("to_person_id")
        to_entity_id = rel.get("to_entity_id")
        rel_type = rel.get("relationship_type")

        if from_person_id not in unique_graph_people_ids:
            add_error(errors, f"People relationship references missing from_person_id: {from_person_id}")
        if bool(to_person_id) == bool(to_entity_id):
            add_error(errors, f"People relationship from {from_person_id} must have exactly one target.")
        if to_person_id and to_person_id not in unique_graph_people_ids:
            add_error(errors, f"People relationship references missing to_person_id: {to_person_id}")
        if to_entity_id and to_entity_id not in org_node_ids:
            add_error(errors, f"People relationship references missing to_entity_id: {to_entity_id}")
        if rel_type not in ALLOWED_PEOPLE_RELATIONSHIPS:
            add_error(errors, f"People relationship from {from_person_id} has unsupported type: {rel_type}")
        if rel_type == "reports_to":
            add_error(errors, "reports_to is not allowed in people_graph_inferred without explicit model expansion.")
        if not rel.get("evidence"):
            add_error(errors, f"People relationship from {from_person_id} has no evidence.")


def validate_outputs(errors: list[str], group: str) -> dict[str, Any]:
    data_dir = DATA_ROOT / group
    payload_path = data_dir / "company_people_research.json"

    require_file(errors, SCHEMA_PATH)
    for file_name in REQUIRED_DATA_FILES:
        require_file(errors, data_dir / file_name)
    for file_name in REQUIRED_DOCS:
        require_file(errors, DOCS_DIR / file_name)

    if not payload_path.exists() or not SCHEMA_PATH.exists():
        return {}

    payload = load_json(payload_path)
    validate_schema(errors, payload)
    validate_org_graph(errors, payload)
    validate_people_graph(errors, payload)
    return payload


def validate_package(errors: list[str], group: str) -> None:
    package_path = DOWNLOADS_DIR / f"{group}_company_research_outputs.zip"
    manifest_path = DATA_ROOT / group / "package_company_research_manifest.json"
    require_file(errors, DATA_ROOT / group / "package_company_research.log.txt")
    require_file(errors, package_path)
    require_file(errors, manifest_path)
    if not package_path.exists() or not manifest_path.exists():
        return

    manifest = load_json(manifest_path)
    expected_files = set(manifest.get("files", []))
    with zipfile.ZipFile(package_path) as archive:
        actual_files = set(archive.namelist())
    missing = sorted(expected_files - actual_files)
    unexpected = sorted(actual_files - expected_files)
    if missing:
        add_error(errors, f"Package is missing files from manifest: {missing}")
    if unexpected:
        add_error(errors, f"Package has files not listed in manifest: {unexpected}")


def write_report(group: str, payload: dict[str, Any], errors: list[str]) -> Path:
    report_path = DATA_ROOT / group / "validate_company_research_outputs_report.json"
    summary = {
        "group": group,
        "valid": not errors,
        "errors": errors,
        "counts": {
            "companies": len(payload.get("companies", [])),
            "people": len(payload.get("people", [])),
            "org_nodes": len(payload.get("org_structure_inferred", {}).get("nodes", [])),
            "org_relationships": len(payload.get("org_structure_inferred", {}).get("relationships", [])),
            "people_graph_nodes": len(payload.get("people_graph_inferred", {}).get("nodes", [])),
            "people_graph_relationships": len(payload.get("people_graph_inferred", {}).get("relationships", [])),
        },
    }
    report_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return report_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate company research generated outputs.")
    parser.add_argument("--group", default="venuiti", help="Group slug to validate.")
    parser.add_argument("--require-package", action="store_true", help="Validate the deterministic zip package.")
    args = parser.parse_args()

    errors: list[str] = []
    payload = validate_outputs(errors, args.group)
    if args.require_package:
        validate_package(errors, args.group)
    report_path = write_report(args.group, payload, errors)

    if errors:
        print(f"company research validation failed; report written to {report_path}")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"company research validation passed; report written to {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
