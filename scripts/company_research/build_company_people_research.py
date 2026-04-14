from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
import sys
from typing import Any

import jsonschema

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.company_research.company_research_data import GROUPS, SCHEMA_VERSION, SIGNAL_WEIGHTS, SNAPSHOT_DATE

DATA_ROOT = ROOT / "data" / "company_research"
SCHEMA_PATH = ROOT / "data" / "schemas" / "company_people_research.schema.json"


def build_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://example.local/schemas/company_people_research.schema.json",
        "title": "Company People Research",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "schema_version",
            "snapshot_date",
            "group_slug",
            "canonical_group",
            "validation_logic",
            "companies",
            "group_relationships",
            "people",
            "risk_flags",
            "interview_alignment_signals",
        ],
        "properties": {
            "schema_version": {"type": "string"},
            "snapshot_date": {"type": "string"},
            "group_slug": {"type": "string"},
            "target_names": {"type": "array", "items": {"type": "string"}},
            "canonical_group": {
                "type": "object",
                "required": [
                    "entity_id",
                    "name",
                    "entity_kind",
                    "validation_status",
                    "confidence",
                    "summary",
                    "evidence_source_ids",
                ],
                "properties": {
                    "entity_id": {"type": "string"},
                    "name": {"type": "string"},
                    "entity_kind": {"type": "string"},
                    "validation_status": {"type": "string"},
                    "confidence": {"type": "number"},
                    "summary": {"type": "string"},
                    "evidence_source_ids": {"type": "array", "items": {"type": "string"}},
                },
                "additionalProperties": False,
            },
            "validation_logic": {
                "type": "object",
                "required": ["signal_weights", "acceptance_rules", "rejection_rules"],
                "properties": {
                    "signal_weights": {"type": "object", "additionalProperties": {"type": "number"}},
                    "acceptance_rules": {"type": "array", "items": {"type": "string"}},
                    "rejection_rules": {"type": "array", "items": {"type": "string"}},
                },
                "additionalProperties": False,
            },
            "companies": {"type": "array", "items": {"$ref": "#/$defs/company"}},
            "group_relationships": {"type": "array", "items": {"$ref": "#/$defs/relationship"}},
            "people": {"type": "array", "items": {"$ref": "#/$defs/person"}},
            "org_structure_inferred": {"$ref": "#/$defs/org_structure_inferred"},
            "people_graph_inferred": {"$ref": "#/$defs/people_graph_inferred"},
            "risk_flags": {"type": "array", "items": {"type": "string"}},
            "interview_alignment_signals": {"type": "array", "items": {"type": "string"}},
        },
        "$defs": {
            "company": {
                "type": "object",
                "required": [
                    "entity_id",
                    "display_name",
                    "entity_kind",
                    "status",
                    "classification",
                    "profile",
                    "source_ids",
                    "interview_signals",
                    "risk_flags",
                ],
                "properties": {
                    "entity_id": {"type": "string"},
                    "display_name": {"type": "string"},
                    "entity_kind": {"type": "string"},
                    "status": {"type": "string"},
                    "classification": {
                        "type": "object",
                        "required": [
                            "canonical_umbrella_name",
                            "legal_style_names",
                            "public_facing_brands",
                            "service_lines",
                        ],
                        "properties": {
                            "canonical_umbrella_name": {"type": "string"},
                            "legal_style_names": {"type": "array", "items": {"type": "string"}},
                            "public_facing_brands": {"type": "array", "items": {"type": "string"}},
                            "service_lines": {"type": "array", "items": {"type": "string"}},
                        },
                        "additionalProperties": False,
                    },
                    "profile": {"type": "object"},
                    "source_ids": {"type": "array", "items": {"type": "string"}},
                    "interview_signals": {"type": "array", "items": {"type": "string"}},
                    "risk_flags": {"type": "array", "items": {"type": "string"}},
                },
                "additionalProperties": False,
            },
            "relationship": {
                "type": "object",
                "required": [
                    "relationship_id",
                    "from_entity_id",
                    "to_entity_id",
                    "relationship_type",
                    "confidence",
                    "decision",
                    "evidence_source_ids",
                    "signals",
                    "cautions",
                ],
                "properties": {
                    "relationship_id": {"type": "string"},
                    "from_entity_id": {"type": "string"},
                    "to_entity_id": {"type": "string"},
                    "relationship_type": {"type": "string"},
                    "confidence": {"type": "number"},
                    "decision": {"type": "string"},
                    "evidence_source_ids": {"type": "array", "items": {"type": "string"}},
                    "signals": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["signal", "strength", "weight", "weighted_score", "source_ids", "notes"],
                            "properties": {
                                "signal": {"type": "string"},
                                "strength": {"type": "number"},
                                "weight": {"type": "number"},
                                "weighted_score": {"type": "number"},
                                "source_ids": {"type": "array", "items": {"type": "string"}},
                                "notes": {"type": "string"},
                            },
                            "additionalProperties": False,
                        },
                    },
                    "cautions": {"type": "array", "items": {"type": "string"}},
                },
                "additionalProperties": False,
            },
            "person": {
                "type": "object",
                "required": [
                    "person_id",
                    "full_name",
                    "normalized_name",
                    "role_summary",
                    "affiliations",
                    "interview_relevance",
                ],
                "properties": {
                    "person_id": {"type": "string"},
                    "full_name": {"type": "string"},
                    "normalized_name": {"type": "string"},
                    "role_summary": {"type": "string"},
                    "affiliations": {"type": "array", "items": {"type": "object"}},
                    "interview_relevance": {"type": "array", "items": {"type": "string"}},
                },
                "additionalProperties": False,
            },
            "org_structure_inferred": {
                "type": "object",
                "required": ["nodes", "relationships"],
                "properties": {
                    "nodes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": [
                                "id",
                                "name",
                                "type",
                                "parent_id",
                                "description",
                                "confidence",
                                "evidence",
                            ],
                            "properties": {
                                "id": {"type": "string"},
                                "name": {"type": "string"},
                                "type": {"type": "string"},
                                "parent_id": {"type": ["string", "null"]},
                                "description": {"type": "string"},
                                "confidence": {"type": "number"},
                                "evidence": {"type": "array", "items": {"type": "string"}},
                            },
                            "additionalProperties": False,
                        },
                    },
                    "relationships": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": [
                                "from_id",
                                "to_id",
                                "relationship_type",
                                "confidence",
                                "evidence",
                            ],
                            "properties": {
                                "from_id": {"type": "string"},
                                "to_id": {"type": "string"},
                                "relationship_type": {"type": "string"},
                                "confidence": {"type": "number"},
                                "evidence": {"type": "array", "items": {"type": "string"}},
                            },
                            "additionalProperties": False,
                        },
                    },
                },
                "additionalProperties": False,
            },
            "people_graph_inferred": {
                "type": "object",
                "required": ["nodes", "relationships"],
                "properties": {
                    "nodes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": [
                                "person_id",
                                "name",
                                "associated_entities",
                                "likely_functions",
                                "confidence",
                            ],
                            "properties": {
                                "person_id": {"type": "string"},
                                "name": {"type": "string"},
                                "associated_entities": {"type": "array", "items": {"type": "string"}},
                                "likely_functions": {"type": "array", "items": {"type": "string"}},
                                "confidence": {"type": "number"},
                            },
                            "additionalProperties": False,
                        },
                    },
                    "relationships": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": [
                                "from_person_id",
                                "relationship_type",
                                "confidence",
                                "evidence",
                            ],
                            "properties": {
                                "from_person_id": {"type": "string"},
                                "to_person_id": {"type": "string"},
                                "to_entity_id": {"type": "string"},
                                "relationship_type": {"type": "string"},
                                "confidence": {"type": "number"},
                                "evidence": {"type": "array", "items": {"type": "string"}},
                            },
                            "anyOf": [
                                {"required": ["to_person_id"]},
                                {"required": ["to_entity_id"]},
                            ],
                            "additionalProperties": False,
                        },
                    },
                },
                "additionalProperties": False,
            },
        },
    }


def configure_logging(log_path: Path) -> logging.Logger:
    logger = logging.getLogger("company_research")
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


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def resolve_relationship(candidate: dict[str, Any]) -> dict[str, Any]:
    scored_signals: list[dict[str, Any]] = []
    evidence_source_ids: list[str] = []
    score = 0.0

    for signal_record in candidate["signals"]:
        signal_name = signal_record["signal"]
        weight = SIGNAL_WEIGHTS[signal_name]
        weighted_score = round(weight * signal_record["strength"], 4)
        score += weighted_score
        evidence_source_ids.extend(signal_record["source_ids"])
        scored_signals.append(
            {
                "signal": signal_name,
                "strength": round(signal_record["strength"], 4),
                "weight": round(weight, 4),
                "weighted_score": weighted_score,
                "source_ids": sorted(set(signal_record["source_ids"])),
                "notes": signal_record["notes"],
            }
        )

    confidence = round(min(score, 0.99), 4)
    if confidence >= 0.8:
        decision = "accepted_high_confidence"
    elif confidence >= 0.6:
        decision = "accepted_with_caution"
    elif confidence >= 0.45:
        decision = "candidate_only"
    else:
        decision = "rejected_weak_match"

    return {
        "relationship_id": candidate["relationship_id"],
        "from_entity_id": candidate["from_entity_id"],
        "to_entity_id": candidate["to_entity_id"],
        "relationship_type": candidate["relationship_type"],
        "confidence": confidence,
        "decision": decision,
        "evidence_source_ids": sorted(set(evidence_source_ids)),
        "signals": scored_signals,
        "cautions": candidate["cautions"],
    }


def build_source_index(group: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "snapshot_date": SNAPSHOT_DATE,
        "group_slug": group["group_slug"],
        "sources": sorted(group["sources"], key=lambda item: item["source_id"]),
    }


def build_people_index(group: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "snapshot_date": SNAPSHOT_DATE,
        "group_slug": group["group_slug"],
        "people": sorted(group["people"], key=lambda item: item["normalized_name"]),
    }


def build_entity_resolution(group: dict[str, Any], relationships: list[dict[str, Any]]) -> dict[str, Any]:
    aliases: list[dict[str, Any]] = []
    for entity in group["entities"]:
        alias_set = sorted(
            set(
                [entity["display_name"]]
                + entity["classification"]["legal_style_names"]
                + entity["classification"]["public_facing_brands"]
            )
        )
        aliases.append(
            {
                "entity_id": entity["entity_id"],
                "display_name": entity["display_name"],
                "aliases": alias_set,
                "canonical_umbrella_name": entity["classification"]["canonical_umbrella_name"],
                "validation_notes": entity["risk_flags"],
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "snapshot_date": SNAPSHOT_DATE,
        "group_slug": group["group_slug"],
        "canonical_group": group["canonical_group"],
        "aliases": sorted(aliases, key=lambda item: item["entity_id"]),
        "relationship_resolution": relationships,
        "rejected_or_unverified_candidates": group["rejects"],
    }


def build_company_people_research(group: dict[str, Any], relationships: list[dict[str, Any]]) -> dict[str, Any]:
    accepted_relationships = [item for item in relationships if item["decision"] != "rejected_weak_match"]
    risk_flags = [
        "Current source set validates the umbrella label 'Venuiti Group of Companies' as public-facing group language, not as an independently verified legal holding-company registration.",
        "DevStaff Canada's exact legal-style entity name remains unresolved in this run.",
        "Shared people, locations, and founding-year overlap are used as corroborating signals only and never as sole proof of ownership.",
    ]
    interview_alignment_signals = [
        "The group appears founder-led and long-running, with 2001 repeatedly cited as the origin point for core operations.",
        "Healthcare interoperability, compliance, staffing, and custom software delivery are recurring themes across the group.",
        "Kitchener-Waterloo is the center of gravity even when brands cite additional geographies such as Atlanta and U.S. client access.",
        "DevStaff is not isolated from the product/services side; official material frames it as an internal-alignment staffing engine for health-tech and Venuiti-branded work.",
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "snapshot_date": SNAPSHOT_DATE,
        "group_slug": group["group_slug"],
        "target_names": group["target_names"],
        "canonical_group": group["canonical_group"],
        "validation_logic": {
            "signal_weights": SIGNAL_WEIGHTS,
            "acceptance_rules": [
                "Accept a relationship as high confidence at 0.80 or above when supported by at least one official-source signal or multiple corroborating signals.",
                "Accept with caution at 0.60 to 0.79 when the evidence set is strong but lacks direct legal-ownership proof.",
                "Keep 0.45 to 0.59 as candidate-only and require more evidence before operational use in ownership-sensitive workflows.",
            ],
            "rejection_rules": [
                "Reject matches below 0.45 as weak or unrelated.",
                "Do not infer legal ownership, control, or reporting lines from shared location, shared people, or shared founding year alone.",
                "Treat LinkedIn company metadata as supporting evidence rather than primary legal proof.",
            ],
        },
        "companies": sorted(group["entities"], key=lambda item: item["display_name"]),
        "group_relationships": accepted_relationships,
        "people": sorted(group["people"], key=lambda item: item["normalized_name"]),
        "org_structure_inferred": group.get("org_structure_inferred", {"nodes": [], "relationships": []}),
        "people_graph_inferred": group.get("people_graph_inferred", {"nodes": [], "relationships": []}),
        "risk_flags": risk_flags,
        "interview_alignment_signals": interview_alignment_signals,
    }


def validate_payload(schema: dict[str, Any], payload: dict[str, Any]) -> None:
    jsonschema.Draft202012Validator(schema).validate(payload)


def build_group(group_slug: str, logger: logging.Logger) -> None:
    if group_slug not in GROUPS:
        raise KeyError(f"Unknown group slug: {group_slug}")

    group = GROUPS[group_slug]
    output_dir = DATA_ROOT / group_slug
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Building schema for group '%s'.", group_slug)
    schema = build_schema()
    write_json(SCHEMA_PATH, schema)

    logger.info("Resolving relationship candidates.")
    relationships = sorted(
        (resolve_relationship(candidate) for candidate in group["relationship_candidates"]),
        key=lambda item: item["relationship_id"],
    )

    source_index = build_source_index(group)
    people_index = build_people_index(group)
    entity_resolution = build_entity_resolution(group, relationships)
    company_people_research = build_company_people_research(group, relationships)

    logger.info("Validating primary normalized payload.")
    validate_payload(schema, company_people_research)

    logger.info("Writing normalized outputs.")
    write_json(output_dir / "source_index.json", source_index)
    write_json(output_dir / "people_index.json", people_index)
    write_json(output_dir / "entity_resolution.json", entity_resolution)
    write_json(output_dir / "company_people_research.json", company_people_research)

    logger.info("Build complete for '%s'.", group_slug)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build normalized company + people research outputs.")
    parser.add_argument("--group", default="venuiti", help="Group slug to build.")
    args = parser.parse_args()

    log_dir = DATA_ROOT / args.group
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = configure_logging(log_dir / "build_company_people_research.log.txt")

    try:
        build_group(args.group, logger)
    except Exception as exc:
        logger.exception("Build failed: %s", exc)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
