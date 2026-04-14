from __future__ import annotations

import json

from career_common import DATA_DIR, get_logger, run_logged, stable_hash, write_json

STORY_GROUPS = {
    "audit_compliance_frameworks": {
        "match_any": {"audit", "compliance", "grc", "security", "sox_soc", "iso27001_27017"},
        "themes": ["controls_assurance", "framework_alignment", "regulatory_readiness"],
        "situation": "Multiple roles required building or repairing control environments in regulated organizations with overlapping framework demands.",
        "task": "Create a control structure leaders could trust without slowing delivery or creating compliance theater.",
        "actions": [
            "Unified overlapping framework requirements into a workable operating model.",
            "Mapped controls, issues, and remediation plans to clearer ownership and reporting.",
            "Used GRC tooling and evidence management to reduce manual coordination and audit friction.",
        ],
        "outcomes": [
            "Improved audit readiness and reduced reactive compliance work.",
            "Created reusable evidence structures that supported downstream reporting and leadership reviews.",
        ],
    },
    "enterprise_risk_vendor_assurance": {
        "match_any": {"third_party_risk", "vendor_management", "grc", "security", "stakeholder_engagement"},
        "themes": ["third_party_risk", "risk_translation", "assurance_at_scale"],
        "situation": "Several roles involved high-volume vendor, technology, and operational risk oversight across business-critical functions.",
        "task": "Scale risk review and vendor assurance without blocking procurement or delivery teams.",
        "actions": [
            "Built practical intake and assessment patterns for third-party and technology risk review.",
            "Translated risk findings into decisions executives, delivery teams, and vendors could act on.",
            "Embedded security and compliance expectations into contracts, governance, and remediation tracking.",
        ],
        "outcomes": [
            "Higher assurance coverage with more consistent decision quality.",
            "Reduced friction between oversight teams and delivery stakeholders.",
        ],
    },
    "program_leadership_transformation": {
        "match_any": {"leadership", "pm", "program_delivery", "stakeholder_engagement"},
        "themes": ["program_delivery", "cross_function_leadership", "operating_model_change"],
        "situation": "Leadership roles repeatedly required stepping into ambiguity, stabilizing delivery, and aligning technical work with business priorities.",
        "task": "Stand up or repair delivery structures that could move work forward across multiple teams and stakeholders.",
        "actions": [
            "Clarified scope, ownership, reporting, and execution cadence across teams.",
            "Used metrics, issue management, and stakeholder communication to keep delivery on track.",
            "Coordinated business, technical, and vendor participants around shared outcomes.",
        ],
        "outcomes": [
            "Greater predictability in delivery and clearer executive visibility.",
            "Improved operating discipline in teams with mixed priorities or immature processes.",
        ],
    },
    "erp_client_implementation": {
        "match_any": {"erp", "consulting", "client_delivery", "implementation", "client_training"},
        "themes": ["erp_delivery", "client_consulting", "requirements_translation"],
        "situation": "Earlier software and HR/payroll roles centered on ERP, HRIS, and custom application delivery for client and operational environments.",
        "task": "Translate business needs into workable system implementations, training, and adoption plans.",
        "actions": [
            "Collected requirements and converted them into actionable implementation and support plans.",
            "Worked directly with clients, users, and technical teams to refine delivery priorities and solutions.",
            "Supported testing, training, rollout, and post-go-live adoption in client-facing settings.",
        ],
        "outcomes": [
            "Better fit between business processes and delivered systems.",
            "Higher client confidence through clearer communication, training, and implementation support.",
        ],
    },
    "training_enablement": {
        "match_any": {"training", "client_training", "education_enablement"},
        "themes": ["enablement", "training", "knowledge_transfer"],
        "situation": "Across speaking, implementation, and support roles, success often depended on helping people understand and use complex systems or practices.",
        "task": "Turn specialist knowledge into usable guidance for mixed technical and non-technical audiences.",
        "actions": [
            "Designed training and presentation content around audience needs and practical application.",
            "Adjusted examples, language, and depth to improve comprehension and adoption.",
            "Used feedback loops to refine delivery and strengthen retention.",
        ],
        "outcomes": [
            "Faster adoption of systems, controls, or operating practices.",
            "Stronger stakeholder trust in both the message and the person delivering it.",
        ],
    },
}


def choose_story_group(role: dict) -> str:
    tags = set(role.get("domains", []) + role.get("capability_tags", []) + role.get("relevance_tags", []))
    for group_id, config in STORY_GROUPS.items():
        if tags & config["match_any"]:
            return group_id
    return "program_leadership_transformation"


def build_story_master(career_master: dict) -> dict:
    employers = {item["employer_id"]: item for item in career_master["employers"]}
    grouped: dict[str, list[dict]] = {}
    for role in career_master["roles"]:
        grouped.setdefault(choose_story_group(role), []).append(role)

    stories = []
    for group_id, roles in sorted(grouped.items()):
        config = STORY_GROUPS[group_id]
        source_roles = sorted({role["role_id"] for role in roles})
        source_employers = sorted({role["employer_id"] for role in roles})
        tools = sorted({item for role in roles for item in role["tools"] + role["frameworks"]})
        domains = sorted({item for role in roles for item in role.get("domains", [])})
        industries = sorted({item for role in roles for item in role.get("industries", [])})
        capabilities = sorted({item for role in roles for item in role.get("capability_tags", [])})
        role_fit_tags = sorted(set(domains + capabilities + [item for role in roles for item in role["relevance_tags"]]))
        source_refs = [ref for role in roles for ref in role["source_references"]]
        strength = round(
            min(
                1.0,
                0.5
                + 0.05 * min(len(source_roles), 5)
                + 0.04 * min(len(tools), 5)
                + 0.03 * min(len(capabilities), 5),
            ),
            2,
        )
        sensitivity = sorted(
            {
                role["suppression_reason"]
                for role in roles
                if role["visibility_default"] == "hidden" or role["suppression_reason"] != "none"
            }
        )
        stories.append(
            {
                "story_id": f"story_{stable_hash(group_id)}",
                "canonical_story_key": group_id,
                "source_roles": source_roles,
                "source_employers": source_employers,
                "domains": domains,
                "industries": industries,
                "capability_tags": capabilities,
                "themes": config["themes"],
                "situation": config["situation"],
                "task": config["task"],
                "actions": config["actions"],
                "outcomes": config["outcomes"],
                "tools_frameworks": tools,
                "audience_fit": sorted(set(["interview_panel", "live_response_generation", "resume_tailoring"] + role_fit_tags)),
                "role_fit_tags": role_fit_tags,
                "strength_score": strength,
                "sensitivity_flags": sensitivity,
                "preferred_when": [
                    f"Use when the target role needs evidence for {tag.replace('_', ' ')}." for tag in role_fit_tags[:6]
                ],
                "avoid_when": [
                    "Avoid when a narrower company-specific story is required downstream."
                ] + (
                    ["Avoid leading with this story unless the downstream opportunity layer explicitly allows hidden-context evidence."]
                    if sensitivity
                    else []
                ),
                "source_references": source_refs,
                "source_role_titles": sorted({role["title"] for role in roles}),
                "source_employer_names": sorted({employers[role["employer_id"]]["display_name"] for role in roles if role["employer_id"] in employers}),
            }
        )
    return {"schema_version": "1.0", "stories": sorted(stories, key=lambda item: item["story_id"])}


def main() -> int:
    logger = get_logger("build_story_master.log.txt")

    def _run() -> None:
        career_master = json.loads((DATA_DIR / "career_master.json").read_text(encoding="utf-8"))
        story_master = build_story_master(career_master)
        write_json(DATA_DIR / "story_master.json", story_master)
        logger.info("wrote %s reusable stories", len(story_master["stories"]))

    return run_logged(logger, _run)


if __name__ == "__main__":
    raise SystemExit(main())
