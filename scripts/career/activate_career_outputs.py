from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path

from career_common import DATA_DIR, ROOT, get_logger, run_logged, write_json

OPPORTUNITY_ROOT = ROOT / "data" / "opportunities" / "venuiti" / "technology_project_manager"
COMPANY_RESEARCH_PATH = ROOT / "data" / "company_research" / "venuiti" / "company_people_research.json"
ALIAS_INDEX_PATH = DATA_DIR / "story_alias_index.json"
ACTIVATION_SUMMARY_PATH = ROOT / "reports" / "data" / "career_activation_summary.json"

ALIAS_MAP = {
    "sun_life_health_and_benefits_delivery": {
        "canonical_story_key": "audit_compliance_frameworks",
        "anchor_role_titles": [
            "SR. PROJECT MANAGEMENT – IT GROUP BENEFITS",
            "SR. PROJECT MANAGER – IT INDIVIDUAL APPLICATIONS",
        ],
        "label": "Sun Life health and benefits delivery",
    },
    "manulife_group_benefits_recovery_project": {
        "canonical_story_key": "audit_compliance_frameworks",
        "anchor_role_titles": [
            "IT RISK MANAGEMENT CONSULTANT, GROUP BENEFITS AND RETIREMENT SOLUTION TECHNOLOGIES",
            "PROJECT RISK MANAGEMENT CONSULTANT, TECHNOLOGY RISK MANAGEMENT, GLOBAL INFORMATION RISK MANAGEMENT",
        ],
        "label": "Manulife group benefits recovery and risk delivery",
    },
    "manulife_internet_release_delivery": {
        "canonical_story_key": "audit_compliance_frameworks",
        "anchor_role_titles": [
            "TEAM LEADER - SERVICE DELIVERY AND SUPPORT",
            "PROJECT MANAGER - INFORMATION SYSTEMS",
        ],
        "label": "Manulife internet and application release delivery",
    },
    "spaenaur_application_portfolio_leadership": {
        "canonical_story_key": "audit_compliance_frameworks",
        "anchor_role_titles": [
            "MANAGER OF APPLICATIONS, DEVELOPMENT AND SUPPORT",
            "DIRECTOR (ACTING) OF INFORMATION SERVICES",
        ],
        "label": "Spaenaur application portfolio leadership",
    },
    "hubble_erp_upgrade_zero_downtime": {
        "canonical_story_key": "enterprise_risk_vendor_assurance",
        "anchor_role_titles": [
            "ERP PROJECT MANAGER AND ERP CONSULTANT",
        ],
        "label": "Hubble ERP implementation and upgrade control",
    },
    "kuntz_hrms_modernization": {
        "canonical_story_key": "audit_compliance_frameworks",
        "anchor_role_titles": [
            "MANAGER OF BUSINESS APPLICATIONS, TRAINING AND SUPPORT",
        ],
        "label": "Kuntz HRMS modernization and support transformation",
    },
    "opentext_security_governance": {
        "canonical_story_key": "audit_compliance_frameworks",
        "anchor_role_titles": [
            "LEAD SECURITY COMPLIANCE ANALYST, GLOBAL INFORMATION SECURITY, GOVERNANCE & RISK",
            "MANAGER INFORMATION SECURITY, GLOBAL INFORMATION SECURITY, GOVERNANCE & RISK",
        ],
        "label": "OpenText security governance and execution discipline",
    },
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def append_unique(items: list, value) -> None:
    if value not in items:
        items.append(value)


def dedupe_scalar_list(items: list) -> list:
    seen = set()
    deduped = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def dedupe_dict_list(items: list[dict], key_fields: tuple[str, ...]) -> list[dict]:
    seen: set[tuple] = set()
    deduped: list[dict] = []
    for item in items:
        key = tuple(item.get(field) for field in key_fields)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def resolve_aliases(career_master: dict, story_master: dict) -> dict:
    stories_by_key = {story["canonical_story_key"]: story for story in story_master["stories"]}
    roles_by_title = {role["title"]: role for role in career_master["roles"]}
    employers = {employer["employer_id"]: employer for employer in career_master["employers"]}
    aliases = {}
    for alias_id, config in ALIAS_MAP.items():
        story = stories_by_key[config["canonical_story_key"]]
        anchor_roles = [
            roles_by_title[title]
            for title in config["anchor_role_titles"]
            if title in roles_by_title
        ]
        aliases[alias_id] = {
            "alias_story_id": alias_id,
            "label": config["label"],
            "canonical_story_id": story["story_id"],
            "canonical_story_key": story["canonical_story_key"],
            "anchor_role_ids": [role["role_id"] for role in anchor_roles],
            "anchor_role_titles": [role["title"] for role in anchor_roles],
            "anchor_employers": sorted(
                {
                    employers[role["employer_id"]]["display_name"]
                    for role in anchor_roles
                    if role["employer_id"] in employers
                }
            ),
            "domains": sorted({item for role in anchor_roles for item in role.get("domains", [])}) or story["domains"],
            "capability_tags": sorted({item for role in anchor_roles for item in role.get("capability_tags", [])}) or story["capability_tags"],
            "sensitivity_flags": story["sensitivity_flags"],
            "resolved_status": "resolved_to_master_story",
        }
    return aliases


def activate_opportunity_profile(opportunity_profile: dict, aliases: dict) -> dict:
    payload = deepcopy(opportunity_profile)
    found = set(payload.get("source_inputs_used", {}).get("found_in_repo", []))
    found.update(
        [
            "data/career/career_master.json",
            "data/career/story_master.json",
            "data/career/story_alias_index.json",
            "data/company_research/venuiti/company_people_research.json",
        ]
    )
    requested_missing = [
        item
        for item in payload.get("source_inputs_used", {}).get("requested_but_missing", [])
        if item not in found
    ]
    payload["source_inputs_used"]["found_in_repo"] = sorted(found)
    payload["source_inputs_used"]["requested_but_missing"] = requested_missing
    for item in payload.get("story_selection_priorities", []):
        alias = aliases.get(item["story_id"])
        if alias:
            item["canonical_story_id"] = alias["canonical_story_id"]
            item["canonical_story_key"] = alias["canonical_story_key"]
            item["anchor_role_ids"] = alias["anchor_role_ids"]
            item["anchor_role_titles"] = alias["anchor_role_titles"]
            item["anchor_employers"] = alias["anchor_employers"]
    validation = payload.setdefault("validation", {})
    validation["notes"] = [
        note
        for note in validation.get("notes", [])
        if "story_master.json is not present" not in note and "missing master-json" not in note.lower()
    ]
    append_unique(
        validation["notes"],
        "Master career and story files are present and the provisional story selections are resolved to canonical master story IDs.",
    )
    validation["notes"] = dedupe_scalar_list(validation["notes"])
    validation["master_story_resolution_complete"] = True
    build_log = payload.setdefault("build_log", [])
    append_unique(
        build_log,
        {
            "step": len(build_log) + 1,
            "action": "Activated provisional story priorities against the canonical career/story warehouse and company research inputs.",
        },
    )
    payload["build_log"] = dedupe_dict_list(build_log, ("action",))
    return payload


def activate_response_bank(response_bank: dict, aliases: dict) -> dict:
    payload = deepcopy(response_bank)
    for item in payload.get("mapped_stories", []):
        alias = aliases.get(item["story_id"])
        if alias:
            item["canonical_story_id"] = alias["canonical_story_id"]
            item["canonical_story_key"] = alias["canonical_story_key"]
            item["anchor_role_ids"] = alias["anchor_role_ids"]
            item["anchor_role_titles"] = alias["anchor_role_titles"]
    for item in payload.get("likely_question_bank", []):
        canonical_ids = []
        for story_id in item.get("mapped_story_ids", []):
            alias = aliases.get(story_id)
            if alias and alias["canonical_story_id"] not in canonical_ids:
                canonical_ids.append(alias["canonical_story_id"])
        item["canonical_story_ids"] = canonical_ids
    validation = payload.setdefault("validation", {})
    validation["mapped_story_source_note"] = (
        "Story mappings are resolved from provisional opportunity aliases to canonical master-story IDs."
    )
    validation["master_story_resolution_complete"] = True
    build_log = payload.setdefault("build_log", [])
    append_unique(
        build_log,
        {
            "step": len(build_log) + 1,
            "action": "Resolved mapped interview stories to canonical master-story IDs and anchor roles.",
        },
    )
    payload["build_log"] = dedupe_dict_list(build_log, ("action",))
    return payload


def activate_live_config(live_config: dict, aliases: dict) -> dict:
    payload = deepcopy(live_config)
    priority_story_order_canonical = []
    for story_id in payload.get("priority_story_order", []):
        if story_id in aliases:
            canonical_story_id = aliases[story_id]["canonical_story_id"]
            if canonical_story_id not in priority_story_order_canonical:
                priority_story_order_canonical.append(canonical_story_id)
    payload["priority_story_order_canonical"] = priority_story_order_canonical
    payload["priority_story_alias_resolution"] = [
        item
        for item in [
            {
                "alias_story_id": story_id,
                "canonical_story_id": aliases[story_id]["canonical_story_id"],
                "anchor_role_titles": aliases[story_id]["anchor_role_titles"],
            }
            for story_id in payload.get("priority_story_order", [])
            if story_id in aliases
        ]
        if item["alias_story_id"] in aliases
    ]
    payload["priority_story_alias_resolution"] = dedupe_dict_list(
        payload["priority_story_alias_resolution"], ("alias_story_id",)
    )
    validation = payload.setdefault("validation", {})
    notes = validation.setdefault("notes", [])
    append_unique(
        notes,
        "Priority story order now includes canonical story resolution for live retrieval systems.",
    )
    validation["notes"] = dedupe_scalar_list(notes)
    build_log = payload.setdefault("build_log", [])
    append_unique(
        build_log,
        {
            "step": len(build_log) + 1,
            "action": "Resolved live interview priority story aliases to canonical master-story IDs.",
        },
    )
    payload["build_log"] = dedupe_dict_list(build_log, ("action",))
    return payload


def main() -> int:
    logger = get_logger("activate_career_outputs.log.txt")

    def _run() -> None:
        career_master = load_json(DATA_DIR / "career_master.json")
        story_master = load_json(DATA_DIR / "story_master.json")
        company_research = load_json(COMPANY_RESEARCH_PATH)
        opportunity_profile = load_json(OPPORTUNITY_ROOT / "opportunity_profile.json")
        response_bank = load_json(OPPORTUNITY_ROOT / "opportunity_interview_response_bank.json")
        live_config = load_json(OPPORTUNITY_ROOT / "live_interview_config.json")

        aliases = resolve_aliases(career_master, story_master)
        alias_index = {
            "schema_version": "1.0",
            "target_group": "venuiti",
            "company_research_entity_id": company_research["canonical_group"]["entity_id"],
            "aliases": sorted(aliases.values(), key=lambda item: item["alias_story_id"]),
        }

        write_json(ALIAS_INDEX_PATH, alias_index)
        activated_profile = activate_opportunity_profile(opportunity_profile, aliases)
        activated_response_bank = activate_response_bank(response_bank, aliases)
        activated_live_config = activate_live_config(live_config, aliases)
        write_json(OPPORTUNITY_ROOT / "opportunity_profile.json", activated_profile)
        write_json(OPPORTUNITY_ROOT / "opportunity_interview_response_bank.json", activated_response_bank)
        write_json(OPPORTUNITY_ROOT / "live_interview_config.json", activated_live_config)
        write_json(
            ACTIVATION_SUMMARY_PATH,
            {
                "schema_version": "1.0",
                "target_group": "venuiti",
                "activated_at_runtime": "deterministic_no_timestamp",
                "company_research_entity_id": company_research["canonical_group"]["entity_id"],
                "resolved_alias_count": len(aliases),
                "canonical_story_ids_used": activated_live_config["priority_story_order_canonical"],
                "output_files": [
                    "data/career/story_alias_index.json",
                    "data/opportunities/venuiti/technology_project_manager/opportunity_profile.json",
                    "data/opportunities/venuiti/technology_project_manager/opportunity_interview_response_bank.json",
                    "data/opportunities/venuiti/technology_project_manager/live_interview_config.json",
                ],
            },
        )
        logger.info("activated opportunity-layer compatibility for %s story aliases", len(aliases))

    return run_logged(logger, _run)


if __name__ == "__main__":
    raise SystemExit(main())
