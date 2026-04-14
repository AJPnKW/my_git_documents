from __future__ import annotations

from typing import Any

SCHEMA_VERSION = "1.0.0"
SNAPSHOT_DATE = "2026-04-09"

SIGNAL_WEIGHTS = {
    "direct_domain_match": 0.28,
    "official_domain_cross_reference": 0.22,
    "explicit_group_language": 0.20,
    "shared_location": 0.12,
    "shared_employee_overlap": 0.10,
    "shared_founding_year": 0.08,
}

GROUPS: dict[str, dict[str, Any]] = {
    "venuiti": {
        "group_slug": "venuiti",
        "target_names": [
            "Venuiti Solutions Inc.",
            "DevStaff Canada",
            "Venuiti Healthcare",
            "Venuiti Group of Companies",
        ],
        "canonical_group": {
            "entity_id": "group_venuiti",
            "name": "Venuiti Group of Companies",
            "entity_kind": "umbrella_group",
            "validation_status": "validated_public_group_name",
            "confidence": 0.87,
            "summary": (
                "Multiple official pages use 'Venuiti Group of Companies' as the umbrella label "
                "for related operating brands. Current evidence supports a public-facing umbrella "
                "name, not a verified legal holding-company conclusion."
            ),
            "evidence_source_ids": [
                "devstaff_meet_thomas",
                "venuiti_health_staffing",
            ],
        },
        "entities": [
            {
                "entity_id": "company_venuiti_solutions",
                "display_name": "Venuiti Solutions Inc.",
                "entity_kind": "company",
                "status": "active",
                "classification": {
                    "canonical_umbrella_name": "Venuiti Group of Companies",
                    "legal_style_names": ["Venuiti Solutions Inc."],
                    "public_facing_brands": ["Venuiti", "Venuiti Solutions"],
                    "service_lines": [
                        "Custom software development",
                        "Digital marketing",
                        "UX/UI",
                        "Production",
                        "Media planning and engagement",
                    ],
                },
                "profile": {
                    "website": "https://www.venuiti.com",
                    "industry": "Software Development",
                    "founded_year": 2001,
                    "headquarters": {
                        "city": "Waterloo",
                        "region": "Ontario",
                        "country": "Canada",
                    },
                    "known_locations": [
                        {
                            "label": "Primary location cited on LinkedIn",
                            "address": "33 Dupont St E, Waterloo, ON N2J 2G8, Canada",
                            "source_id": "venuiti_solutions_linkedin",
                        },
                        {
                            "label": "Postal/contact address on privacy policy",
                            "address": "283 Duke St. W., Suite 214, Kitchener, ON N2H 3X7, Canada",
                            "source_id": "venuiti_solutions_privacy",
                        },
                    ],
                    "company_size_range": "11-50 employees",
                    "ownership_language": "Privately Held",
                    "business_description": (
                        "Software development and digital marketing firm describing itself as "
                        "a team combining storytelling, strategy, and technical delivery."
                    ),
                },
                "source_ids": [
                    "venuiti_solutions_privacy",
                    "venuiti_solutions_linkedin",
                    "venuiti_why_canada",
                ],
                "interview_signals": [
                    "Founder-led and long-running business dating to 2001.",
                    "Maintains both technology delivery and marketing-oriented capabilities.",
                    "Strong Kitchener-Waterloo presence with U.S.-facing positioning.",
                ],
                "risk_flags": [
                    "Official website evidence confirms the name and contact address, but detailed corporate registry data was not independently verified in this run.",
                    "LinkedIn supplies founding year, Waterloo headquarters, and overlapping employee data; treat those fields as supporting evidence rather than primary legal proof.",
                ],
            },
            {
                "entity_id": "company_devstaff_canada",
                "display_name": "DevStaff Canada",
                "entity_kind": "company",
                "status": "active",
                "classification": {
                    "canonical_umbrella_name": "Venuiti Group of Companies",
                    "legal_style_names": [],
                    "public_facing_brands": ["DevStaff Canada", "DevStaff"],
                    "service_lines": [
                        "Technical staffing",
                        "Tech recruiting",
                        "IT staffing",
                        "Healthcare staffing",
                        "Temporary staffing",
                        "Permanent staffing",
                        "Full cycle recruitment",
                    ],
                },
                "profile": {
                    "website": "https://devstaff.ca",
                    "industry": "Staffing and Recruiting",
                    "founded_year": 2010,
                    "headquarters": {
                        "city": "Kitchener",
                        "region": "Ontario",
                        "country": "Canada",
                    },
                    "known_locations": [
                        {
                            "label": "Main office cited on contact page",
                            "address": "283 Duke St W, Kitchener, ON N2H 3X7, Canada",
                            "source_id": "devstaff_contact",
                        },
                        {
                            "label": "LinkedIn headquarters",
                            "address": "Kitchener, Ontario, Canada",
                            "source_id": "devstaff_linkedin",
                        },
                    ],
                    "company_size_range": "51-200 employees",
                    "ownership_language": "LinkedIn lists Public Company; official site does not independently confirm this legal classification.",
                    "business_description": (
                        "Boutique technical staffing agency focused on developer and health-tech recruiting."
                    ),
                },
                "source_ids": [
                    "devstaff_contact",
                    "devstaff_linkedin",
                    "devstaff_meet_thomas",
                    "venuiti_health_staffing",
                ],
                "interview_signals": [
                    "Staffing narrative is closely connected to internal technology roots rather than generic recruiting.",
                    "Official pages repeatedly position DevStaff as a health-tech staffing partner.",
                    "Recent public posts reference hiring for roles at Venuiti, indicating operational alignment with the broader group.",
                ],
                "risk_flags": [
                    "No independent registry source was captured for the exact legal entity name in this run, so the legal-style name remains unresolved.",
                    "LinkedIn's 'Public Company' label conflicts with the absence of equivalent language on official pages and should not be treated as ownership proof.",
                ],
            },
            {
                "entity_id": "company_venuiti_healthcare",
                "display_name": "Venuiti Healthcare",
                "entity_kind": "company",
                "status": "active",
                "classification": {
                    "canonical_umbrella_name": "Venuiti Group of Companies",
                    "legal_style_names": ["Venuiti Healthcare Inc."],
                    "public_facing_brands": ["Venuiti Healthcare", "Venuiti Health"],
                    "service_lines": [
                        "Healthcare software development",
                        "Interoperability",
                        "Conformance tooling",
                        "Testing",
                        "Health-tech staffing",
                        "Strategic consulting",
                    ],
                },
                "profile": {
                    "website": "https://venuitihealth.com",
                    "industry": "Software Development",
                    "founded_year": 2001,
                    "headquarters": {
                        "city": "Waterloo",
                        "region": "Ontario",
                        "country": "Canada",
                    },
                    "known_locations": [
                        {
                            "label": "Primary location",
                            "address": "33 Dupont St E, Waterloo, ON N2J 2G8, Canada",
                            "source_id": "venuiti_health_linkedin",
                        },
                        {
                            "label": "Additional operating geography",
                            "address": "Atlanta, Georgia, United States",
                            "source_id": "venuiti_health_contact",
                        },
                    ],
                    "company_size_range": "11-50 employees",
                    "ownership_language": "Privately Held",
                    "business_description": (
                        "Healthcare-focused software and interoperability delivery brand with strong emphasis "
                        "on FHIR, compliance, security, and custom health-tech implementation."
                    ),
                },
                "source_ids": [
                    "venuiti_health_contact",
                    "venuiti_health_services",
                    "venuiti_health_staffing",
                    "venuiti_health_linkedin",
                ],
                "interview_signals": [
                    "Healthcare specialization is deep, not incidental: interoperability, conformance, testing, and consulting appear repeatedly.",
                    "Messaging emphasizes long-term client relationships, private ownership, and healthcare-specific compliance literacy.",
                    "Cross-brand staffing integration with DevStaff is explicit on official pages.",
                ],
                "risk_flags": [
                    "The legal-style name 'Venuiti Healthcare Inc.' is evidenced by page copyright language, which is useful but not equal to a registry filing.",
                    "Relationship to Venuiti Solutions is supported by strong overlap signals and group references, but direct ownership structure is still not independently verified.",
                ],
            },
        ],
        "people": [
            {
                "person_id": "person_thomas_schroecker",
                "full_name": "Thomas Schroecker",
                "normalized_name": "thomas schroecker",
                "role_summary": "Founder / CEO-level leader associated with the Venuiti group and multiple operating brands.",
                "affiliations": [
                    {
                        "entity_id": "group_venuiti",
                        "role_title": "CEO",
                        "relationship_type": "executive",
                        "confidence": 0.94,
                        "source_ids": ["devstaff_meet_thomas"],
                    },
                    {
                        "entity_id": "company_venuiti_solutions",
                        "role_title": "Employee / leadership presence",
                        "relationship_type": "leadership_overlap",
                        "confidence": 0.75,
                        "source_ids": ["venuiti_solutions_linkedin"],
                    },
                    {
                        "entity_id": "company_devstaff_canada",
                        "role_title": "CEO here at DevStaff Canada",
                        "relationship_type": "executive",
                        "confidence": 0.91,
                        "source_ids": ["devstaff_meet_thomas", "devstaff_linkedin"],
                    },
                    {
                        "entity_id": "company_venuiti_healthcare",
                        "role_title": "Employee / leadership presence",
                        "relationship_type": "leadership_overlap",
                        "confidence": 0.72,
                        "source_ids": ["venuiti_health_linkedin"],
                    },
                ],
                "interview_relevance": [
                    "Likely central decision-maker or culture carrier across the group.",
                    "Signals founder-led operating style and continuity across business lines.",
                ],
            },
            {
                "person_id": "person_alexey_sidelnikov",
                "full_name": "Alexey Sidelnikov",
                "normalized_name": "alexey sidelnikov",
                "role_summary": "Technology leader appearing across multiple Venuiti-linked brands.",
                "affiliations": [
                    {
                        "entity_id": "group_venuiti",
                        "role_title": "CTO",
                        "relationship_type": "executive",
                        "confidence": 0.9,
                        "source_ids": ["linkedin_people_snapshot_20260409"],
                    },
                    {
                        "entity_id": "company_venuiti_solutions",
                        "role_title": "CTO / employee presence",
                        "relationship_type": "leadership_overlap",
                        "confidence": 0.86,
                        "source_ids": ["linkedin_people_snapshot_20260409", "venuiti_solutions_linkedin"],
                    },
                    {
                        "entity_id": "company_devstaff_canada",
                        "role_title": "CTO / employee presence",
                        "relationship_type": "leadership_overlap",
                        "confidence": 0.83,
                        "source_ids": ["linkedin_people_snapshot_20260409", "devstaff_linkedin"],
                    },
                    {
                        "entity_id": "company_venuiti_healthcare",
                        "role_title": "CTO / group technology leadership overlap",
                        "relationship_type": "leadership_overlap",
                        "confidence": 0.8,
                        "source_ids": ["linkedin_people_snapshot_20260409"],
                    },
                ],
                "interview_relevance": [
                    "Strong evidence of cross-brand technical leadership rather than simple employee overlap.",
                ],
            },
            {
                "person_id": "person_jordan_schroecker",
                "full_name": "Jordan Schroecker",
                "normalized_name": "jordan schroecker",
                "role_summary": "Cross-brand operations and recruiting leader visible in DevStaff and Venuiti Healthcare contexts.",
                "affiliations": [
                    {
                        "entity_id": "group_venuiti",
                        "role_title": "Director of Operations",
                        "relationship_type": "executive",
                        "confidence": 0.88,
                        "source_ids": ["linkedin_people_snapshot_20260409"],
                    },
                    {
                        "entity_id": "company_devstaff_canada",
                        "role_title": "Director of Operations",
                        "relationship_type": "executive",
                        "confidence": 0.87,
                        "source_ids": ["linkedin_people_snapshot_20260409", "devstaff_linkedin"],
                    },
                    {
                        "entity_id": "company_venuiti_healthcare",
                        "role_title": "Director of Operations",
                        "relationship_type": "executive",
                        "confidence": 0.84,
                        "source_ids": ["linkedin_people_snapshot_20260409", "venuiti_health_linkedin"],
                    }
                ],
                "interview_relevance": [
                    "Useful bridge person between operations, technical recruiting, healthcare, and fintech narratives across the group.",
                ],
            },
            {
                "person_id": "person_shannon_teeter",
                "full_name": "Shannon Teeter",
                "normalized_name": "shannon teeter",
                "role_summary": "Executive-level group operator visible in DevStaff and Venuiti Healthcare adjacency.",
                "affiliations": [
                    {
                        "entity_id": "group_venuiti",
                        "role_title": "Executive",
                        "relationship_type": "executive",
                        "confidence": 0.82,
                        "source_ids": ["linkedin_people_snapshot_20260409", "devstaff_linkedin"],
                    },
                    {
                        "entity_id": "company_devstaff_canada",
                        "role_title": "Executive presence",
                        "relationship_type": "leadership_overlap",
                        "confidence": 0.73,
                        "source_ids": ["linkedin_people_snapshot_20260409", "devstaff_linkedin"],
                    },
                    {
                        "entity_id": "company_venuiti_healthcare",
                        "role_title": "Executive presence",
                        "relationship_type": "leadership_overlap",
                        "confidence": 0.69,
                        "source_ids": ["linkedin_people_snapshot_20260409"],
                    },
                ],
                "interview_relevance": [
                    "Adds evidence of a broader executive/operator layer beyond founder-only leadership.",
                ],
            },
            {
                "person_id": "person_sneha_gontu",
                "full_name": "Sneha Gontu",
                "normalized_name": "sneha gontu",
                "role_summary": "Talent acquisition specialist repeatedly surfaced in Venuiti / DevStaff-linked LinkedIn people lists.",
                "affiliations": [
                    {
                        "entity_id": "company_devstaff_canada",
                        "role_title": "Talent Acquisition Specialist",
                        "relationship_type": "employee",
                        "confidence": 0.56,
                        "source_ids": ["linkedin_people_snapshot_20260409"],
                    }
                ],
                "interview_relevance": [
                    "Suggests recruiting capacity beyond founder-level and operations leadership, but entity mapping remains cautious.",
                ],
            },
            {
                "person_id": "person_brent_mcnatt",
                "full_name": "Brent McNatt",
                "normalized_name": "brent mcnatt",
                "role_summary": "Full stack engineer appearing across Venuiti Healthcare and Venuiti Solutions.",
                "affiliations": [
                    {
                        "entity_id": "company_venuiti_healthcare",
                        "role_title": "Full Stack Developer",
                        "relationship_type": "employee",
                        "confidence": 0.78,
                        "source_ids": ["linkedin_people_snapshot_20260409"],
                    },
                    {
                        "entity_id": "company_venuiti_solutions",
                        "role_title": "Full Stack Developer",
                        "relationship_type": "employee",
                        "confidence": 0.78,
                        "source_ids": ["linkedin_people_snapshot_20260409"],
                    },
                ],
                "interview_relevance": [
                    "Supports real technical talent overlap between the healthcare and solutions entities.",
                ],
            },
            {
                "person_id": "person_melissa_shariff",
                "full_name": "Melissa Shariff",
                "normalized_name": "melissa shariff",
                "role_summary": "Senior operations manager visible at Venuiti Group of Companies.",
                "affiliations": [
                    {
                        "entity_id": "group_venuiti",
                        "role_title": "Sr. Manager of Operations / Project Manager",
                        "relationship_type": "executive",
                        "confidence": 0.8,
                        "source_ids": ["linkedin_people_snapshot_20260409"],
                    }
                ],
                "interview_relevance": [
                    "Strengthens the evidence for a formal operations layer inside the broader group.",
                ],
            },
            {
                "person_id": "person_susanne_roma",
                "full_name": "Susanne Roma",
                "normalized_name": "susanne roma",
                "role_summary": "General manager tied directly to Venuiti Solutions Inc.",
                "affiliations": [
                    {
                        "entity_id": "company_venuiti_solutions",
                        "role_title": "General Manager",
                        "relationship_type": "executive",
                        "confidence": 0.82,
                        "source_ids": ["linkedin_people_snapshot_20260409"],
                    }
                ],
                "interview_relevance": [
                    "Suggests mature delivery/operations management inside Venuiti Solutions itself.",
                ],
            },
            {
                "person_id": "person_anhad_lamba",
                "full_name": "Anhad Lamba",
                "normalized_name": "anhad lamba",
                "role_summary": "AI-oriented full stack developer associated with Venuiti.",
                "affiliations": [
                    {
                        "entity_id": "company_venuiti_solutions",
                        "role_title": "AI Full Stack Developer",
                        "relationship_type": "employee",
                        "confidence": 0.72,
                        "source_ids": ["linkedin_people_snapshot_20260409"],
                    }
                ],
                "interview_relevance": [
                    "Supports an emerging AI/full-stack engineering specialization inside the Venuiti Solutions side of the group.",
                ],
            },
            {
                "person_id": "person_shiv_patel",
                "full_name": "Shiv Patel",
                "normalized_name": "shiv patel",
                "role_summary": "AI developer associated with Venuiti.",
                "affiliations": [
                    {
                        "entity_id": "company_venuiti_solutions",
                        "role_title": "AI Developer",
                        "relationship_type": "employee",
                        "confidence": 0.69,
                        "source_ids": ["linkedin_people_snapshot_20260409"],
                    }
                ],
                "interview_relevance": [
                    "Further supports an AI-oriented delivery capability, but exact sub-team structure remains inferred rather than explicit.",
                ],
            },
            {
                "person_id": "person_jordan_hagedorn",
                "full_name": "Jordan Hagedorn",
                "normalized_name": "jordan hagedorn",
                "role_summary": "AI-oriented full stack developer tied to Venuiti Solutions.",
                "affiliations": [
                    {
                        "entity_id": "company_venuiti_solutions",
                        "role_title": "Full Stack AI Developer",
                        "relationship_type": "employee",
                        "confidence": 0.73,
                        "source_ids": ["linkedin_people_snapshot_20260409"],
                    }
                ],
                "interview_relevance": [
                    "Adds repeated evidence for AI/full-stack engineering talent in Venuiti Solutions.",
                ],
            },
            {
                "person_id": "person_madison_weber",
                "full_name": "Madison Weber",
                "normalized_name": "madison weber",
                "role_summary": "Front-end / React developer tied to Venuiti Solutions.",
                "affiliations": [
                    {
                        "entity_id": "company_venuiti_solutions",
                        "role_title": "React Developer",
                        "relationship_type": "employee",
                        "confidence": 0.7,
                        "source_ids": ["linkedin_people_snapshot_20260409"],
                    }
                ],
                "interview_relevance": [
                    "Supports a modern web product engineering capability in the solutions entity.",
                ],
            },
            {
                "person_id": "person_gabriela_pereira",
                "full_name": "Gabriela Pereira",
                "normalized_name": "gabriela pereira",
                "role_summary": "Software developer tied to Venuiti Solutions.",
                "affiliations": [
                    {
                        "entity_id": "company_venuiti_solutions",
                        "role_title": "Software Developer",
                        "relationship_type": "employee",
                        "confidence": 0.7,
                        "source_ids": ["linkedin_people_snapshot_20260409"],
                    }
                ],
                "interview_relevance": [
                    "Adds depth to the identified engineering bench inside Venuiti Solutions.",
                ],
            },
            {
                "person_id": "person_dmytro_lavrentiev",
                "full_name": "Dmytro Lavrentiev",
                "normalized_name": "dmytro lavrentiev",
                "role_summary": "Senior software developer associated with Venuiti Healthcare.",
                "affiliations": [
                    {
                        "entity_id": "company_venuiti_healthcare",
                        "role_title": "Senior Software Developer",
                        "relationship_type": "employee",
                        "confidence": 0.76,
                        "source_ids": ["linkedin_people_snapshot_20260409"],
                    }
                ],
                "interview_relevance": [
                    "Supports the inference that Venuiti Healthcare has an actual in-house software engineering team, not only staffing/consulting language.",
                ],
            },
            {
                "person_id": "person_pleiades_chambers",
                "full_name": "Pleiades Chambers",
                "normalized_name": "pleiades chambers",
                "role_summary": "Junior project manager associated with Venuiti.",
                "affiliations": [
                    {
                        "entity_id": "company_venuiti_healthcare",
                        "role_title": "Junior Project Manager",
                        "relationship_type": "employee",
                        "confidence": 0.62,
                        "source_ids": ["linkedin_people_snapshot_20260409"],
                    }
                ],
                "interview_relevance": [
                    "Suggests dedicated project coordination capacity near the healthcare side, though entity mapping remains cautious.",
                ],
            },
        ],
        "relationship_candidates": [
            {
                "relationship_id": "rel_group_to_devstaff",
                "from_entity_id": "group_venuiti",
                "to_entity_id": "company_devstaff_canada",
                "relationship_type": "umbrella_member",
                "signals": [
                    {
                        "signal": "official_domain_cross_reference",
                        "strength": 1.0,
                        "source_ids": ["venuiti_health_staffing"],
                        "notes": "Venuiti Healthcare explicitly names DevStaff Canada as a member of the Venuiti Group of Companies.",
                    },
                    {
                        "signal": "explicit_group_language",
                        "strength": 1.0,
                        "source_ids": ["devstaff_meet_thomas"],
                        "notes": "DevStaff profile content uses Venuiti Group of Companies as umbrella language.",
                    },
                    {
                        "signal": "shared_employee_overlap",
                        "strength": 0.7,
                        "source_ids": ["devstaff_linkedin", "venuiti_solutions_linkedin"],
                        "notes": "Thomas Schroecker and Alexey Sidelnikov appear across related brands.",
                    },
                    {
                        "signal": "shared_location",
                        "strength": 0.7,
                        "source_ids": ["devstaff_contact", "venuiti_solutions_privacy"],
                        "notes": "Kitchener/Waterloo office corridor overlap is strong.",
                    },
                ],
                "cautions": [],
            },
            {
                "relationship_id": "rel_group_to_venuiti_solutions",
                "from_entity_id": "group_venuiti",
                "to_entity_id": "company_venuiti_solutions",
                "relationship_type": "umbrella_member",
                "signals": [
                    {
                        "signal": "direct_domain_match",
                        "strength": 1.0,
                        "source_ids": ["venuiti_solutions_privacy"],
                        "notes": "Official venuiti.com page names Venuiti Solutions.",
                    },
                    {
                        "signal": "explicit_group_language",
                        "strength": 0.85,
                        "source_ids": ["devstaff_meet_thomas"],
                        "notes": "Thomas article describes the original 2001 company and the broader Venuiti Group together.",
                    },
                    {
                        "signal": "shared_employee_overlap",
                        "strength": 0.8,
                        "source_ids": ["venuiti_solutions_linkedin", "devstaff_linkedin"],
                        "notes": "Thomas Schroecker and Alexey Sidelnikov overlap with related brands.",
                    },
                    {
                        "signal": "shared_founding_year",
                        "strength": 1.0,
                        "source_ids": ["venuiti_solutions_linkedin", "devstaff_meet_thomas"],
                        "notes": "The 2001 origin story aligns with the core Venuiti business.",
                    },
                ],
                "cautions": [
                    "This supports group membership and continuity, but does not independently establish a legal parent company filing.",
                ],
            },
            {
                "relationship_id": "rel_group_to_venuiti_healthcare",
                "from_entity_id": "group_venuiti",
                "to_entity_id": "company_venuiti_healthcare",
                "relationship_type": "umbrella_member",
                "signals": [
                    {
                        "signal": "direct_domain_match",
                        "strength": 1.0,
                        "source_ids": ["venuiti_health_contact", "venuiti_health_staffing"],
                        "notes": "Official venuitihealth.com pages directly identify the brand.",
                    },
                    {
                        "signal": "shared_employee_overlap",
                        "strength": 0.65,
                        "source_ids": ["venuiti_health_linkedin", "venuiti_solutions_linkedin"],
                        "notes": "Thomas Schroecker is visible on both brand profiles.",
                    },
                    {
                        "signal": "shared_location",
                        "strength": 1.0,
                        "source_ids": ["venuiti_health_linkedin", "venuiti_solutions_linkedin"],
                        "notes": "Both brands cite 33 Dupont St E, Waterloo, Ontario.",
                    },
                    {
                        "signal": "shared_founding_year",
                        "strength": 1.0,
                        "source_ids": ["venuiti_health_linkedin", "venuiti_solutions_linkedin"],
                        "notes": "Both LinkedIn profiles cite 2001.",
                    },
                ],
                "cautions": [
                    "No single official page in the source set directly states that Venuiti Healthcare is a legal subsidiary of a parent entity.",
                ],
            },
            {
                "relationship_id": "rel_venuiti_health_to_devstaff",
                "from_entity_id": "company_venuiti_healthcare",
                "to_entity_id": "company_devstaff_canada",
                "relationship_type": "exclusive_staffing_partner",
                "signals": [
                    {
                        "signal": "official_domain_cross_reference",
                        "strength": 1.0,
                        "source_ids": ["venuiti_health_staffing"],
                        "notes": "Venuiti Healthcare says it works exclusively with DevStaff Canada.",
                    },
                    {
                        "signal": "explicit_group_language",
                        "strength": 1.0,
                        "source_ids": ["venuiti_health_staffing"],
                        "notes": "The same page calls DevStaff a member of the Venuiti Group of Companies.",
                    },
                    {
                        "signal": "shared_location",
                        "strength": 0.7,
                        "source_ids": ["venuiti_health_contact", "devstaff_contact"],
                        "notes": "Both operate in the Kitchener-Waterloo region.",
                    },
                ],
                "cautions": [],
            },
            {
                "relationship_id": "rel_venuiti_solutions_to_devstaff",
                "from_entity_id": "company_venuiti_solutions",
                "to_entity_id": "company_devstaff_canada",
                "relationship_type": "group_peer_alignment",
                "signals": [
                    {
                        "signal": "shared_employee_overlap",
                        "strength": 0.8,
                        "source_ids": ["venuiti_solutions_linkedin", "devstaff_linkedin"],
                        "notes": "Thomas Schroecker and Alexey Sidelnikov appear on both profiles.",
                    },
                    {
                        "signal": "shared_location",
                        "strength": 0.8,
                        "source_ids": ["venuiti_solutions_privacy", "devstaff_contact"],
                        "notes": "Shared Kitchener-area address cluster.",
                    },
                    {
                        "signal": "shared_founding_year",
                        "strength": 0.8,
                        "source_ids": ["venuiti_solutions_linkedin", "devstaff_meet_thomas"],
                        "notes": "DevStaff is described as a later expansion from the earlier Venuiti operation.",
                    },
                ],
                "cautions": [
                    "Treat as strong operating-group alignment, not direct proof of legal ownership.",
                ],
            },
        ],
        "rejects": [
            {
                "candidate_name": "Venuiti Group of Companies as a legally registered holding company",
                "decision": "not_verified",
                "reason": (
                    "Current evidence validates the phrase as a public-facing umbrella descriptor, "
                    "but no registry filing or equivalent primary legal source was captured."
                ),
                "confidence": 0.22,
            },
            {
                "candidate_name": "Direct reporting-line hierarchy between DevStaff Canada and Venuiti Healthcare",
                "decision": "rejected",
                "reason": (
                    "Official pages show collaboration and exclusive staffing partnership, but they do not "
                    "prove that one brand legally reports into the other."
                ),
                "confidence": 0.16,
            },
        ],
        "org_structure_inferred": {
            "nodes": [
                {
                    "id": "group_venuiti",
                    "name": "Venuiti Group of Companies",
                    "type": "brand",
                    "parent_id": None,
                    "description": "Public-facing umbrella identity used across related Venuiti operating brands.",
                    "confidence": 0.87,
                    "evidence": [
                        "devstaff_meet_thomas: official DevStaff page calls Thomas Schroecker CEO at Venuiti Group of Companies.",
                        "venuiti_health_staffing: official Venuiti Healthcare page calls DevStaff Canada a member of the Venuiti Group of Companies.",
                    ],
                },
                {
                    "id": "function_group_executive_leadership",
                    "name": "Group Executive Leadership",
                    "type": "function",
                    "parent_id": "group_venuiti",
                    "description": "Executive leadership layer inferred from repeated group-level CEO, CTO, and executive titles.",
                    "confidence": 0.86,
                    "evidence": [
                        "devstaff_meet_thomas: Thomas Schroecker is named CEO at Venuiti Group of Companies.",
                        "linkedin_people_snapshot_20260409: Alexey Sidelnikov is described as CTO at Venuiti Group of Companies and Shannon Teeter as Executive @ Venuiti Group of Companies.",
                    ],
                },
                {
                    "id": "function_group_operations",
                    "name": "Group Operations",
                    "type": "function",
                    "parent_id": "group_venuiti",
                    "description": "Shared operations layer inferred from group-level operations titles spanning multiple brands.",
                    "confidence": 0.82,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Jordan Schroecker is described as Director of Operations @ Venuiti Group of Companies, DevStaff Canada & Venuiti Healthcare.",
                        "linkedin_people_snapshot_20260409: Melissa Shariff is listed as Sr. Manager of Operations @ Venuiti Group of Companies.",
                    ],
                },
                {
                    "id": "brand_venuiti",
                    "name": "Venuiti",
                    "type": "brand",
                    "parent_id": "group_venuiti",
                    "description": "Primary public-facing Venuiti brand used alongside Venuiti Solutions in official materials.",
                    "confidence": 0.84,
                    "evidence": [
                        "venuiti_solutions_privacy: official venuiti.com page uses Venuiti branding on the site for Venuiti Solutions Inc.",
                        "venuiti_why_canada: DevStaff page references Venuiti as the long-running technology business behind the broader operating story.",
                    ],
                },
                {
                    "id": "company_venuiti_solutions",
                    "name": "Venuiti Solutions Inc.",
                    "type": "company",
                    "parent_id": "group_venuiti",
                    "description": "Core software and digital delivery company associated with the broader Venuiti group.",
                    "confidence": 0.61,
                    "evidence": [
                        "venuiti_solutions_privacy: official venuiti.com page names Venuiti Solutions Inc.",
                        "devstaff_meet_thomas: official article ties the original custom software business to the broader Venuiti story.",
                    ],
                },
                {
                    "id": "function_venuiti_solutions_digital_delivery",
                    "name": "Digital and Software Delivery",
                    "type": "function",
                    "parent_id": "company_venuiti_solutions",
                    "description": "Combined custom software, UX/UI, production, and media delivery capability inferred from public service-line language.",
                    "confidence": 0.78,
                    "evidence": [
                        "company_people_research existing service lines list custom software development, UX/UI, production, and media planning and engagement.",
                        "venuiti_why_canada: DevStaff page positions Venuiti as a long-running technology business with U.S.-facing operations.",
                    ],
                },
                {
                    "id": "function_venuiti_solutions_ai_engineering",
                    "name": "AI and Applied Engineering",
                    "type": "function",
                    "parent_id": "company_venuiti_solutions",
                    "description": "AI-oriented engineering capability inferred from repeated public employee titles referencing AI developers and AI full-stack developers.",
                    "confidence": 0.73,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Anhad Lamba is listed as AI Full Stack Developer @ Venuiti.",
                        "linkedin_people_snapshot_20260409: Shiv Patel is listed as AI Developer at Venuiti and Jordan Hagedorn as Full Stack AI Developer at Venuiti Solutions.",
                    ],
                },
                {
                    "id": "team_venuiti_solutions_frontend_web",
                    "name": "Frontend and Web Delivery",
                    "type": "team",
                    "parent_id": "function_venuiti_solutions_digital_delivery",
                    "description": "Web and frontend implementation cluster inferred from repeated React and software developer profiles tied to Venuiti Solutions.",
                    "confidence": 0.69,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Madison Weber is listed as React Developer at Venuiti Solutions Inc.",
                        "linkedin_people_snapshot_20260409: Gabriela Pereira is listed as Software Developer @ Venuiti Solutions.",
                    ],
                },
                {
                    "id": "company_devstaff_canada",
                    "name": "DevStaff Canada",
                    "type": "company",
                    "parent_id": "group_venuiti",
                    "description": "Staffing and recruiting brand aligned with the Venuiti group, especially for technical and healthcare roles.",
                    "confidence": 0.574,
                    "evidence": [
                        "devstaff_meet_thomas: official page uses Venuiti Group of Companies language.",
                        "venuiti_health_staffing: official Venuiti Healthcare page calls DevStaff Canada a member of the group.",
                    ],
                },
                {
                    "id": "brand_devstaff",
                    "name": "DevStaff",
                    "type": "brand",
                    "parent_id": "company_devstaff_canada",
                    "description": "Short-form staffing brand used publicly alongside the full DevStaff Canada company name.",
                    "confidence": 0.82,
                    "evidence": [
                        "devstaff_contact: official site branding uses DevStaff while contact details map to DevStaff Canada.",
                        "devstaff_linkedin: public company profile uses DevStaff Canada and DevStaff interchangeably in branding context.",
                    ],
                },
                {
                    "id": "function_devstaff_staffing",
                    "name": "Staffing and Recruitment",
                    "type": "function",
                    "parent_id": "company_devstaff_canada",
                    "description": "Technical, healthcare, temporary, and permanent recruiting function run under DevStaff Canada.",
                    "confidence": 0.9,
                    "evidence": [
                        "company_people_research existing service lines list technical staffing, healthcare staffing, temporary staffing, permanent staffing, and full cycle recruitment.",
                        "venuiti_health_staffing: Venuiti Healthcare says it works exclusively with DevStaff Canada for staffing.",
                    ],
                },
                {
                    "id": "team_devstaff_talent_acquisition",
                    "name": "Talent Acquisition",
                    "type": "team",
                    "parent_id": "function_devstaff_staffing",
                    "description": "Dedicated recruiting team inferred from repeated talent acquisition and recruitment coordinator profiles associated with DevStaff and Venuiti Solutions.",
                    "confidence": 0.67,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Sneha Gontu is listed as Talent Acquisition Specialist.",
                        "linkedin_people_snapshot_20260409: Shannon Schroecker is listed as Recruitment Coordinator at Venuiti Solutions Inc., indicating an active recruiting function in the same operating environment.",
                    ],
                },
                {
                    "id": "company_venuiti_healthcare",
                    "name": "Venuiti Healthcare",
                    "type": "company",
                    "parent_id": "group_venuiti",
                    "description": "Healthcare-focused software and interoperability brand within the public Venuiti umbrella.",
                    "confidence": 0.545,
                    "evidence": [
                        "venuiti_health_contact: official domain directly identifies the brand.",
                        "venuiti_health_linkedin and venuiti_solutions_linkedin: shared Waterloo location and founding year support close operating alignment.",
                    ],
                },
                {
                    "id": "brand_venuiti_health",
                    "name": "Venuiti Health",
                    "type": "brand",
                    "parent_id": "company_venuiti_healthcare",
                    "description": "Short-form public-facing healthcare brand used interchangeably with Venuiti Healthcare.",
                    "confidence": 0.81,
                    "evidence": [
                        "company_people_research existing classification lists Venuiti Health as a public-facing brand.",
                        "venuiti_health_contact and venuiti_health_services: official domain uses Venuiti Healthcare while the broader shorthand Venuiti Health appears in classification and public references.",
                    ],
                },
                {
                    "id": "department_vh_engineering_integration",
                    "name": "Engineering and Integration",
                    "type": "department",
                    "parent_id": "company_venuiti_healthcare",
                    "description": "Inferred healthcare delivery unit covering software engineering, interface work, and implementation.",
                    "confidence": 0.84,
                    "evidence": [
                        "company_people_research existing service lines list healthcare software development, interoperability, and testing.",
                        "venuiti_health_services: official services page groups software development, interoperability work, and consulting together.",
                    ],
                },
                {
                    "id": "department_vh_compliance_conformance",
                    "name": "Compliance and Conformance",
                    "type": "department",
                    "parent_id": "company_venuiti_healthcare",
                    "description": "Inferred function focused on conformance tooling, standards work, and healthcare compliance support.",
                    "confidence": 0.82,
                    "evidence": [
                        "company_people_research existing service lines include conformance tooling.",
                        "venuiti_health_services: official services page emphasizes compliance and interoperability support.",
                    ],
                },
                {
                    "id": "function_vh_consulting_strategy",
                    "name": "Healthcare Consulting and Strategy",
                    "type": "function",
                    "parent_id": "company_venuiti_healthcare",
                    "description": "Inferred healthcare consulting and strategic advisory capability paired with implementation and standards work.",
                    "confidence": 0.76,
                    "evidence": [
                        "company_people_research existing service lines include strategic consulting.",
                        "venuiti_health_services: official services page groups consulting with healthcare software, interoperability, and compliance-oriented delivery.",
                    ],
                },
                {
                    "id": "team_vh_project_delivery",
                    "name": "Project Delivery",
                    "type": "team",
                    "parent_id": "company_venuiti_healthcare",
                    "description": "Project coordination and delivery team inferred from project management profiles associated with Venuiti Healthcare and the broader group.",
                    "confidence": 0.64,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Pleiades Chambers is listed as Junior Project Manager at Venuiti.",
                        "linkedin_people_snapshot_20260409: Melissa Shariff is listed as Sr. Manager of Operations @ Venuiti Group of Companies | Project Manager.",
                    ],
                },
            ],
            "relationships": [
                {
                    "from_id": "group_venuiti",
                    "to_id": "function_group_executive_leadership",
                    "relationship_type": "operates_within",
                    "confidence": 0.86,
                    "evidence": [
                        "Repeated group-level executive titles support an inferred executive leadership function without asserting a formal legal org chart.",
                    ],
                },
                {
                    "from_id": "group_venuiti",
                    "to_id": "function_group_operations",
                    "relationship_type": "operates_within",
                    "confidence": 0.82,
                    "evidence": [
                        "Multiple operations titles reference Venuiti Group of Companies directly and span more than one operating entity.",
                    ],
                },
                {
                    "from_id": "group_venuiti",
                    "to_id": "brand_venuiti",
                    "relationship_type": "belongs_to",
                    "confidence": 0.84,
                    "evidence": [
                        "Official Venuiti materials use the Venuiti name as a public-facing brand under the broader umbrella identity.",
                    ],
                },
                {
                    "from_id": "group_venuiti",
                    "to_id": "company_venuiti_solutions",
                    "relationship_type": "belongs_to",
                    "confidence": 0.61,
                    "evidence": [
                        "rel_group_to_venuiti_solutions: accepted_with_caution in the existing relationship model.",
                    ],
                },
                {
                    "from_id": "company_venuiti_solutions",
                    "to_id": "function_venuiti_solutions_digital_delivery",
                    "relationship_type": "operates_within",
                    "confidence": 0.78,
                    "evidence": [
                        "Venuiti Solutions public service-line mix supports a blended digital and software delivery function.",
                    ],
                },
                {
                    "from_id": "company_venuiti_solutions",
                    "to_id": "function_venuiti_solutions_ai_engineering",
                    "relationship_type": "operates_within",
                    "confidence": 0.73,
                    "evidence": [
                        "Repeated AI-oriented employee titles support an inferred AI and applied engineering capability in Venuiti Solutions.",
                    ],
                },
                {
                    "from_id": "function_venuiti_solutions_digital_delivery",
                    "to_id": "team_venuiti_solutions_frontend_web",
                    "relationship_type": "operates_within",
                    "confidence": 0.69,
                    "evidence": [
                        "Repeated React and software developer titles support a distinct frontend and web delivery cluster.",
                    ],
                },
                {
                    "from_id": "group_venuiti",
                    "to_id": "company_devstaff_canada",
                    "relationship_type": "belongs_to",
                    "confidence": 0.574,
                    "evidence": [
                        "rel_group_to_devstaff: candidate_only because the umbrella label is public-facing rather than legally verified.",
                    ],
                },
                {
                    "from_id": "company_devstaff_canada",
                    "to_id": "brand_devstaff",
                    "relationship_type": "operates_within",
                    "confidence": 0.82,
                    "evidence": [
                        "DevStaff branding appears as the public short-form brand for DevStaff Canada on official pages and LinkedIn.",
                    ],
                },
                {
                    "from_id": "company_devstaff_canada",
                    "to_id": "function_devstaff_staffing",
                    "relationship_type": "operates_within",
                    "confidence": 0.9,
                    "evidence": [
                        "DevStaff service-line evidence strongly supports a dedicated staffing and recruitment function.",
                    ],
                },
                {
                    "from_id": "function_devstaff_staffing",
                    "to_id": "team_devstaff_talent_acquisition",
                    "relationship_type": "operates_within",
                    "confidence": 0.67,
                    "evidence": [
                        "Repeated talent acquisition and recruiting titles support a recruiting sub-team within the broader staffing function.",
                    ],
                },
                {
                    "from_id": "group_venuiti",
                    "to_id": "company_venuiti_healthcare",
                    "relationship_type": "belongs_to",
                    "confidence": 0.545,
                    "evidence": [
                        "rel_group_to_venuiti_healthcare: candidate_only because the umbrella label is public-facing rather than legally verified.",
                    ],
                },
                {
                    "from_id": "company_venuiti_healthcare",
                    "to_id": "brand_venuiti_health",
                    "relationship_type": "operates_within",
                    "confidence": 0.81,
                    "evidence": [
                        "Venuiti Health appears as a short-form public-facing brand for Venuiti Healthcare.",
                    ],
                },
                {
                    "from_id": "company_venuiti_healthcare",
                    "to_id": "department_vh_engineering_integration",
                    "relationship_type": "operates_within",
                    "confidence": 0.84,
                    "evidence": [
                        "Venuiti Healthcare service lines explicitly support engineering and integration-oriented work.",
                    ],
                },
                {
                    "from_id": "company_venuiti_healthcare",
                    "to_id": "department_vh_compliance_conformance",
                    "relationship_type": "operates_within",
                    "confidence": 0.82,
                    "evidence": [
                        "Venuiti Healthcare service lines explicitly support compliance and conformance work.",
                    ],
                },
                {
                    "from_id": "company_venuiti_healthcare",
                    "to_id": "function_vh_consulting_strategy",
                    "relationship_type": "operates_within",
                    "confidence": 0.76,
                    "evidence": [
                        "Venuiti Healthcare service lines and services page support a distinct consulting and strategy capability.",
                    ],
                },
                {
                    "from_id": "company_venuiti_healthcare",
                    "to_id": "team_vh_project_delivery",
                    "relationship_type": "operates_within",
                    "confidence": 0.64,
                    "evidence": [
                        "Project-management titles support a lightweight project delivery team inference on the healthcare side.",
                    ],
                },
                {
                    "from_id": "function_group_operations",
                    "to_id": "team_devstaff_talent_acquisition",
                    "relationship_type": "supports",
                    "confidence": 0.66,
                    "evidence": [
                        "Jordan Schroecker's group-level operations title plus DevStaff talent-acquisition profiles imply operational support for recruiting work across entities.",
                    ],
                },
                {
                    "from_id": "function_group_operations",
                    "to_id": "team_vh_project_delivery",
                    "relationship_type": "supports",
                    "confidence": 0.62,
                    "evidence": [
                        "Group operations and project-management titles imply a shared operating support layer for healthcare delivery, but not a formal reporting line.",
                    ],
                },
                {
                    "from_id": "function_devstaff_staffing",
                    "to_id": "department_vh_engineering_integration",
                    "relationship_type": "cross_function",
                    "confidence": 0.504,
                    "evidence": [
                        "rel_venuiti_health_to_devstaff: official page says Venuiti Healthcare works exclusively with DevStaff Canada.",
                    ],
                },
                {
                    "from_id": "function_devstaff_staffing",
                    "to_id": "function_vh_consulting_strategy",
                    "relationship_type": "supports",
                    "confidence": 0.48,
                    "evidence": [
                        "Official Venuiti Healthcare staffing language implies DevStaff recruiting support also feeds consulting and advisory delivery needs, but this remains an inferred operational link.",
                    ],
                },
                {
                    "from_id": "function_venuiti_solutions_ai_engineering",
                    "to_id": "department_vh_engineering_integration",
                    "relationship_type": "cross_function",
                    "confidence": 0.45,
                    "evidence": [
                        "Cross-entity engineering overlap is suggested by shared technical leadership and healthcare engineering profiles, but the sub-team relationship remains low-confidence.",
                    ],
                },
            ],
        },
        "people_graph_inferred": {
            "nodes": [
                {
                    "person_id": "person_thomas_schroecker",
                    "name": "Thomas Schroecker",
                    "associated_entities": [
                        "group_venuiti",
                        "function_group_executive_leadership",
                        "brand_venuiti",
                        "brand_devstaff",
                        "brand_venuiti_health",
                        "company_devstaff_canada",
                        "company_venuiti_solutions",
                        "company_venuiti_healthcare",
                    ],
                    "likely_functions": [
                        "executive leadership",
                        "group strategy",
                        "cross-brand business oversight",
                    ],
                    "confidence": 0.92,
                },
                {
                    "person_id": "person_alexey_sidelnikov",
                    "name": "Alexey Sidelnikov",
                    "associated_entities": [
                        "group_venuiti",
                        "function_group_executive_leadership",
                        "company_devstaff_canada",
                        "company_venuiti_solutions",
                        "company_venuiti_healthcare",
                    ],
                    "likely_functions": [
                        "technology leadership",
                        "cross-brand engineering oversight",
                        "applied delivery strategy",
                    ],
                    "confidence": 0.86,
                },
                {
                    "person_id": "person_jordan_schroecker",
                    "name": "Jordan Schroecker",
                    "associated_entities": [
                        "group_venuiti",
                        "function_group_operations",
                        "company_devstaff_canada",
                        "company_venuiti_healthcare",
                        "team_devstaff_talent_acquisition",
                    ],
                    "likely_functions": [
                        "operations",
                        "technical recruiting",
                        "cross-entity coordination",
                    ],
                    "confidence": 0.86,
                },
                {
                    "person_id": "person_shannon_teeter",
                    "name": "Shannon Teeter",
                    "associated_entities": [
                        "group_venuiti",
                        "function_group_executive_leadership",
                        "company_devstaff_canada",
                        "company_venuiti_healthcare",
                    ],
                    "likely_functions": [
                        "executive leadership",
                        "cross-entity operations",
                    ],
                    "confidence": 0.78,
                },
                {
                    "person_id": "person_melissa_shariff",
                    "name": "Melissa Shariff",
                    "associated_entities": [
                        "group_venuiti",
                        "function_group_operations",
                        "team_vh_project_delivery",
                    ],
                    "likely_functions": [
                        "operations management",
                        "project delivery",
                    ],
                    "confidence": 0.8,
                },
                {
                    "person_id": "person_sneha_gontu",
                    "name": "Sneha Gontu",
                    "associated_entities": [
                        "company_devstaff_canada",
                        "function_devstaff_staffing",
                        "team_devstaff_talent_acquisition",
                    ],
                    "likely_functions": [
                        "talent acquisition",
                        "recruiting",
                    ],
                    "confidence": 0.63,
                },
                {
                    "person_id": "person_susanne_roma",
                    "name": "Susanne Roma",
                    "associated_entities": [
                        "company_venuiti_solutions",
                        "function_venuiti_solutions_digital_delivery",
                    ],
                    "likely_functions": [
                        "general management",
                        "delivery operations",
                    ],
                    "confidence": 0.78,
                },
                {
                    "person_id": "person_brent_mcnatt",
                    "name": "Brent McNatt",
                    "associated_entities": [
                        "company_venuiti_healthcare",
                        "company_venuiti_solutions",
                        "department_vh_engineering_integration",
                    ],
                    "likely_functions": [
                        "full-stack engineering",
                        "cross-entity technical delivery",
                    ],
                    "confidence": 0.78,
                },
                {
                    "person_id": "person_anhad_lamba",
                    "name": "Anhad Lamba",
                    "associated_entities": [
                        "company_venuiti_solutions",
                        "function_venuiti_solutions_ai_engineering",
                    ],
                    "likely_functions": [
                        "ai engineering",
                        "full-stack development",
                    ],
                    "confidence": 0.72,
                },
                {
                    "person_id": "person_shiv_patel",
                    "name": "Shiv Patel",
                    "associated_entities": [
                        "company_venuiti_solutions",
                        "function_venuiti_solutions_ai_engineering",
                    ],
                    "likely_functions": [
                        "ai engineering",
                    ],
                    "confidence": 0.69,
                },
                {
                    "person_id": "person_jordan_hagedorn",
                    "name": "Jordan Hagedorn",
                    "associated_entities": [
                        "company_venuiti_solutions",
                        "function_venuiti_solutions_ai_engineering",
                    ],
                    "likely_functions": [
                        "ai engineering",
                        "full-stack development",
                    ],
                    "confidence": 0.73,
                },
                {
                    "person_id": "person_madison_weber",
                    "name": "Madison Weber",
                    "associated_entities": [
                        "company_venuiti_solutions",
                        "function_venuiti_solutions_digital_delivery",
                        "team_venuiti_solutions_frontend_web",
                    ],
                    "likely_functions": [
                        "frontend engineering",
                        "react development",
                    ],
                    "confidence": 0.7,
                },
                {
                    "person_id": "person_gabriela_pereira",
                    "name": "Gabriela Pereira",
                    "associated_entities": [
                        "company_venuiti_solutions",
                        "function_venuiti_solutions_digital_delivery",
                        "team_venuiti_solutions_frontend_web",
                    ],
                    "likely_functions": [
                        "software development",
                        "web delivery",
                    ],
                    "confidence": 0.7,
                },
                {
                    "person_id": "person_dmytro_lavrentiev",
                    "name": "Dmytro Lavrentiev",
                    "associated_entities": [
                        "company_venuiti_healthcare",
                        "department_vh_engineering_integration",
                    ],
                    "likely_functions": [
                        "software engineering",
                        "healthcare delivery engineering",
                    ],
                    "confidence": 0.76,
                },
                {
                    "person_id": "person_pleiades_chambers",
                    "name": "Pleiades Chambers",
                    "associated_entities": [
                        "company_venuiti_healthcare",
                        "team_vh_project_delivery",
                    ],
                    "likely_functions": [
                        "project management",
                        "delivery coordination",
                    ],
                    "confidence": 0.62,
                },
            ],
            "relationships": [
                {
                    "from_person_id": "person_thomas_schroecker",
                    "to_entity_id": "group_venuiti",
                    "relationship_type": "associated_with",
                    "confidence": 0.94,
                    "evidence": [
                        "devstaff_meet_thomas: official page calls Thomas Schroecker CEO at Venuiti Group of Companies.",
                    ],
                },
                {
                    "from_person_id": "person_thomas_schroecker",
                    "to_entity_id": "function_group_executive_leadership",
                    "relationship_type": "associated_with",
                    "confidence": 0.9,
                    "evidence": [
                        "Group-level CEO title is strong evidence for executive-leadership association.",
                    ],
                },
                {
                    "from_person_id": "person_thomas_schroecker",
                    "to_entity_id": "company_devstaff_canada",
                    "relationship_type": "associated_with",
                    "confidence": 0.91,
                    "evidence": [
                        "devstaff_meet_thomas: official page says he is CEO here at DevStaff Canada.",
                        "devstaff_linkedin: company profile shows Thomas Schroecker among employees.",
                    ],
                },
                {
                    "from_person_id": "person_thomas_schroecker",
                    "to_entity_id": "company_venuiti_solutions",
                    "relationship_type": "cross_entity",
                    "confidence": 0.75,
                    "evidence": [
                        "venuiti_solutions_linkedin: Thomas Schroecker appears on the Venuiti Solutions profile.",
                    ],
                },
                {
                    "from_person_id": "person_thomas_schroecker",
                    "to_entity_id": "company_venuiti_healthcare",
                    "relationship_type": "cross_entity",
                    "confidence": 0.72,
                    "evidence": [
                        "venuiti_health_linkedin: Thomas Schroecker appears on the Venuiti Healthcare profile.",
                    ],
                },
                {
                    "from_person_id": "person_alexey_sidelnikov",
                    "to_entity_id": "group_venuiti",
                    "relationship_type": "associated_with",
                    "confidence": 0.9,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Alexey Sidelnikov is listed as CTO at Venuiti Group of Companies.",
                    ],
                },
                {
                    "from_person_id": "person_alexey_sidelnikov",
                    "to_entity_id": "function_group_executive_leadership",
                    "relationship_type": "associated_with",
                    "confidence": 0.87,
                    "evidence": [
                        "CTO title is strong evidence for executive and technology leadership association.",
                    ],
                },
                {
                    "from_person_id": "person_alexey_sidelnikov",
                    "to_entity_id": "company_venuiti_solutions",
                    "relationship_type": "associated_with",
                    "confidence": 0.86,
                    "evidence": [
                        "linkedin_people_snapshot_20260409 and venuiti_solutions_linkedin: Alexey Sidelnikov is surfaced in the Venuiti Solutions context.",
                    ],
                },
                {
                    "from_person_id": "person_alexey_sidelnikov",
                    "to_entity_id": "company_devstaff_canada",
                    "relationship_type": "cross_entity",
                    "confidence": 0.83,
                    "evidence": [
                        "linkedin_people_snapshot_20260409 and devstaff_linkedin: Alexey Sidelnikov is surfaced in the DevStaff Canada context.",
                    ],
                },
                {
                    "from_person_id": "person_alexey_sidelnikov",
                    "to_entity_id": "company_venuiti_healthcare",
                    "relationship_type": "cross_entity",
                    "confidence": 0.8,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Alexey Sidelnikov's CTO title is stated across Venuiti Healthcare, Venuiti Solutions, and DevStaff Canada.",
                    ],
                },
                {
                    "from_person_id": "person_jordan_schroecker",
                    "to_entity_id": "group_venuiti",
                    "relationship_type": "associated_with",
                    "confidence": 0.88,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Jordan Schroecker is listed as Director of Operations @ Venuiti Group of Companies.",
                    ],
                },
                {
                    "from_person_id": "person_jordan_schroecker",
                    "to_entity_id": "function_group_operations",
                    "relationship_type": "associated_with",
                    "confidence": 0.86,
                    "evidence": [
                        "Group-level Director of Operations title is strong evidence for operations-function association.",
                    ],
                },
                {
                    "from_person_id": "person_jordan_schroecker",
                    "to_entity_id": "company_devstaff_canada",
                    "relationship_type": "associated_with",
                    "confidence": 0.87,
                    "evidence": [
                        "linkedin_people_snapshot_20260409 and devstaff_linkedin: Jordan Schroecker is listed in the DevStaff Canada context.",
                    ],
                },
                {
                    "from_person_id": "person_jordan_schroecker",
                    "to_entity_id": "company_venuiti_healthcare",
                    "relationship_type": "cross_entity",
                    "confidence": 0.84,
                    "evidence": [
                        "linkedin_people_snapshot_20260409 and venuiti_health_linkedin: Jordan Schroecker is listed in the Venuiti Healthcare context.",
                    ],
                },
                {
                    "from_person_id": "person_shannon_teeter",
                    "to_entity_id": "group_venuiti",
                    "relationship_type": "associated_with",
                    "confidence": 0.82,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Shannon Teeter is listed as Executive @ Venuiti Group of Companies.",
                    ],
                },
                {
                    "from_person_id": "person_shannon_teeter",
                    "to_entity_id": "function_group_executive_leadership",
                    "relationship_type": "associated_with",
                    "confidence": 0.79,
                    "evidence": [
                        "Executive title is strong evidence for an executive-leadership association.",
                    ],
                },
                {
                    "from_person_id": "person_melissa_shariff",
                    "to_entity_id": "group_venuiti",
                    "relationship_type": "associated_with",
                    "confidence": 0.8,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Melissa Shariff is listed as Sr. Manager of Operations @ Venuiti Group of Companies.",
                    ],
                },
                {
                    "from_person_id": "person_melissa_shariff",
                    "to_entity_id": "function_group_operations",
                    "relationship_type": "associated_with",
                    "confidence": 0.8,
                    "evidence": [
                        "Operations manager title directly supports group operations association.",
                    ],
                },
                {
                    "from_person_id": "person_sneha_gontu",
                    "to_entity_id": "team_devstaff_talent_acquisition",
                    "relationship_type": "associated_with",
                    "confidence": 0.63,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Sneha Gontu is listed as Talent Acquisition Specialist connecting with professionals in KW and the GTA.",
                    ],
                },
                {
                    "from_person_id": "person_susanne_roma",
                    "to_entity_id": "company_venuiti_solutions",
                    "relationship_type": "associated_with",
                    "confidence": 0.82,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Susanne Roma is listed as General Manager at Venuiti Solutions Inc.",
                    ],
                },
                {
                    "from_person_id": "person_brent_mcnatt",
                    "to_entity_id": "company_venuiti_healthcare",
                    "relationship_type": "associated_with",
                    "confidence": 0.78,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Brent McNatt is listed as Full Stack Developer | Venuiti Healthcare | Venuiti Solutions.",
                    ],
                },
                {
                    "from_person_id": "person_brent_mcnatt",
                    "to_entity_id": "company_venuiti_solutions",
                    "relationship_type": "cross_entity",
                    "confidence": 0.78,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Brent McNatt profile explicitly references both Venuiti Healthcare and Venuiti Solutions.",
                    ],
                },
                {
                    "from_person_id": "person_anhad_lamba",
                    "to_entity_id": "function_venuiti_solutions_ai_engineering",
                    "relationship_type": "associated_with",
                    "confidence": 0.72,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Anhad Lamba is listed as AI Full Stack Developer @ Venuiti.",
                    ],
                },
                {
                    "from_person_id": "person_shiv_patel",
                    "to_entity_id": "function_venuiti_solutions_ai_engineering",
                    "relationship_type": "associated_with",
                    "confidence": 0.69,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Shiv Patel is listed as AI Developer at Venuiti.",
                    ],
                },
                {
                    "from_person_id": "person_jordan_hagedorn",
                    "to_entity_id": "function_venuiti_solutions_ai_engineering",
                    "relationship_type": "associated_with",
                    "confidence": 0.73,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Jordan Hagedorn is listed as Full Stack AI Developer at Venuiti Solutions.",
                    ],
                },
                {
                    "from_person_id": "person_madison_weber",
                    "to_entity_id": "team_venuiti_solutions_frontend_web",
                    "relationship_type": "associated_with",
                    "confidence": 0.7,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Madison Weber is listed as React Developer at Venuiti Solutions Inc.",
                    ],
                },
                {
                    "from_person_id": "person_gabriela_pereira",
                    "to_entity_id": "team_venuiti_solutions_frontend_web",
                    "relationship_type": "associated_with",
                    "confidence": 0.7,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Gabriela Pereira is listed as Software Developer @ Venuiti Solutions.",
                    ],
                },
                {
                    "from_person_id": "person_dmytro_lavrentiev",
                    "to_entity_id": "department_vh_engineering_integration",
                    "relationship_type": "associated_with",
                    "confidence": 0.76,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Dmytro Lavrentiev is listed as Senior Software Developer @ Venuiti Healthcare.",
                    ],
                },
                {
                    "from_person_id": "person_pleiades_chambers",
                    "to_entity_id": "team_vh_project_delivery",
                    "relationship_type": "associated_with",
                    "confidence": 0.62,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Pleiades Chambers is listed as Junior Project Manager at Venuiti.",
                    ],
                },
                {
                    "from_person_id": "person_thomas_schroecker",
                    "to_person_id": "person_alexey_sidelnikov",
                    "relationship_type": "works_with",
                    "confidence": 0.83,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Thomas Schroecker and Alexey Sidelnikov are both described with group-level executive titles.",
                        "devstaff_linkedin and venuiti_solutions_linkedin: both people appear in the same multi-entity operating environment.",
                    ],
                },
                {
                    "from_person_id": "person_thomas_schroecker",
                    "to_person_id": "person_jordan_schroecker",
                    "relationship_type": "works_with",
                    "confidence": 0.74,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: Thomas Schroecker and Jordan Schroecker are both presented in group-level and cross-entity operating contexts.",
                    ],
                },
                {
                    "from_person_id": "person_jordan_schroecker",
                    "to_person_id": "person_shannon_teeter",
                    "relationship_type": "works_with",
                    "confidence": 0.68,
                    "evidence": [
                        "devstaff_linkedin and venuiti_health_linkedin: both people appear in overlapping group-linked entity contexts.",
                    ],
                },
                {
                    "from_person_id": "person_jordan_schroecker",
                    "to_person_id": "person_melissa_shariff",
                    "relationship_type": "works_with",
                    "confidence": 0.71,
                    "evidence": [
                        "linkedin_people_snapshot_20260409: both hold operations titles in the broader Venuiti Group operating context.",
                    ],
                },
                {
                    "from_person_id": "person_jordan_schroecker",
                    "to_person_id": "person_sneha_gontu",
                    "relationship_type": "works_with",
                    "confidence": 0.58,
                    "evidence": [
                        "Jordan Schroecker's recruiting-oriented operations title and Sneha Gontu's talent acquisition title support a cautious recruiting-team collaboration inference.",
                    ],
                },
                {
                    "from_person_id": "person_anhad_lamba",
                    "to_person_id": "person_shiv_patel",
                    "relationship_type": "likely_same_team",
                    "confidence": 0.63,
                    "evidence": [
                        "Both profiles use AI-focused developer titles tied to Venuiti in the same public snapshot.",
                    ],
                },
                {
                    "from_person_id": "person_anhad_lamba",
                    "to_person_id": "person_jordan_hagedorn",
                    "relationship_type": "likely_same_team",
                    "confidence": 0.65,
                    "evidence": [
                        "Both profiles use AI full-stack developer language tied to Venuiti Solutions / Venuiti.",
                    ],
                },
                {
                    "from_person_id": "person_madison_weber",
                    "to_person_id": "person_gabriela_pereira",
                    "relationship_type": "likely_same_team",
                    "confidence": 0.61,
                    "evidence": [
                        "Both profiles place them in software or frontend development at Venuiti Solutions.",
                    ],
                },
                {
                    "from_person_id": "person_brent_mcnatt",
                    "to_person_id": "person_dmytro_lavrentiev",
                    "relationship_type": "works_with",
                    "confidence": 0.59,
                    "evidence": [
                        "Both profiles place them in hands-on software engineering work tied to Venuiti Healthcare.",
                    ],
                },
            ],
        },
        "sources": [
            {
                "source_id": "venuiti_solutions_privacy",
                "title": "Privacy - Venuiti Solutions Inc.",
                "url": "https://www.venuiti.com/privacy/",
                "source_type": "official_website",
                "publisher": "Venuiti Solutions Inc.",
                "domain": "venuiti.com",
                "snapshot_date": SNAPSHOT_DATE,
                "key_points": [
                    "Page chrome names Venuiti Solutions Inc.",
                    "Postal mail address lists 283 Duke St. W., Suite 214, Kitchener, ON N2H 3X7.",
                    "Phone number listed as 1-866-819-9155.",
                ],
            },
            {
                "source_id": "venuiti_solutions_linkedin",
                "title": "Venuiti Solutions Inc. | LinkedIn",
                "url": "https://ca.linkedin.com/company/venuiti-solutions-inc.",
                "source_type": "linkedin_profile",
                "publisher": "LinkedIn",
                "domain": "linkedin.com",
                "snapshot_date": SNAPSHOT_DATE,
                "key_points": [
                    "Headquarters listed as Waterloo, Ontario.",
                    "Founded year listed as 2001.",
                    "Primary location listed as 33 Dupont St E, Waterloo, ON N2J 2G8.",
                    "Employees shown include Thomas Schroecker and Alexey Sidelnikov.",
                ],
            },
            {
                "source_id": "venuiti_why_canada",
                "title": "Why Canada – DevStaff",
                "url": "https://devstaff.ca/why-canada/",
                "source_type": "official_website",
                "publisher": "DevStaff",
                "domain": "devstaff.ca",
                "snapshot_date": SNAPSHOT_DATE,
                "key_points": [
                    "Page states Venuiti has been in business since 2001-era timing.",
                    "Page positions Venuiti as Canada-based with U.S. locations.",
                ],
            },
            {
                "source_id": "devstaff_contact",
                "title": "Contact Us – DevStaff",
                "url": "https://devstaff.ca/contact-us/",
                "source_type": "official_website",
                "publisher": "DevStaff",
                "domain": "devstaff.ca",
                "snapshot_date": SNAPSHOT_DATE,
                "key_points": [
                    "Contact page asks 'Looking to find out more about Venuiti?'",
                    "Main office listed as 283 Duke St W, Kitchener, ON N2H 3X7.",
                    "Page says Venuiti has been in business since 2001.",
                ],
            },
            {
                "source_id": "devstaff_linkedin",
                "title": "DevStaff Canada | LinkedIn",
                "url": "https://ca.linkedin.com/company/devstaff-canada",
                "source_type": "linkedin_profile",
                "publisher": "LinkedIn",
                "domain": "linkedin.com",
                "snapshot_date": SNAPSHOT_DATE,
                "key_points": [
                    "Headquarters listed as Kitchener, Ontario.",
                    "Employees shown include Alexey Sidelnikov, Thomas Schroecker, Shannon Teeter, and Jordan Schroecker.",
                    "Recent posts reference hiring for roles at Venuiti.",
                ],
            },
            {
                "source_id": "devstaff_meet_thomas",
                "title": "Meet Thomas Schroecker CEO at Venuiti Group of Companies – DevStaff",
                "url": "https://devstaff.ca/p-meet-thomas-schroecker-ceo-at-venuiti-group-of-companies/",
                "source_type": "official_website",
                "publisher": "DevStaff",
                "domain": "devstaff.ca",
                "snapshot_date": SNAPSHOT_DATE,
                "key_points": [
                    "Calls Thomas Schroecker the CEO at Venuiti Group of Companies.",
                    "States he runs three successful startups under Venuiti Group of Companies.",
                    "Explains DevStaff was added after roughly 10 years of prior custom software development work.",
                    "References the healthcare aspect of the company as part of the same broader story.",
                ],
            },
            {
                "source_id": "venuiti_health_contact",
                "title": "Contact Us – Venuiti Healthcare",
                "url": "https://venuitihealth.com/contact-us/",
                "source_type": "official_website",
                "publisher": "Venuiti Healthcare",
                "domain": "venuitihealth.com",
                "snapshot_date": SNAPSHOT_DATE,
                "key_points": [
                    "Page brands the company as Venuiti Healthcare.",
                    "States the company has multiple locations in Waterloo, Canada and Atlanta, Georgia.",
                    "States the company is 100% privately owned.",
                    "Footer copyright says Venuiti Healthcare Inc.",
                ],
            },
            {
                "source_id": "venuiti_health_services",
                "title": "Our Services – Venuiti Healthcare",
                "url": "https://venuitihealth.com/our-services/",
                "source_type": "official_website",
                "publisher": "Venuiti Healthcare",
                "domain": "venuitihealth.com",
                "snapshot_date": SNAPSHOT_DATE,
                "key_points": [
                    "States nearly two decades of dedicated service in healthcare software development.",
                    "Lists interoperability, compliance, staffing, and strategic consulting service lines.",
                    "Says end-to-end staffing is offered in collaboration with DevStaff Canada.",
                ],
            },
            {
                "source_id": "venuiti_health_staffing",
                "title": "Staffing – Venuiti Healthcare",
                "url": "https://venuitihealth.com/staffing/",
                "source_type": "official_website",
                "publisher": "Venuiti Healthcare",
                "domain": "venuitihealth.com",
                "snapshot_date": SNAPSHOT_DATE,
                "key_points": [
                    "States Venuiti Healthcare works exclusively with DevStaff Canada.",
                    "Explicitly identifies DevStaff Canada as a member of the Venuiti Group of Companies.",
                    "Footer copyright says Venuiti Healthcare Inc.",
                ],
            },
            {
                "source_id": "venuiti_health_linkedin",
                "title": "Venuiti Healthcare | LinkedIn",
                "url": "https://www.linkedin.com/company/venuitihealthcare",
                "source_type": "linkedin_profile",
                "publisher": "LinkedIn",
                "domain": "linkedin.com",
                "snapshot_date": SNAPSHOT_DATE,
                "key_points": [
                    "Headquarters listed as Waterloo, Ontario.",
                    "Founded year listed as 2001.",
                    "Primary location listed as 33 Dupont St E, Waterloo, ON N2J 2G8.",
                    "Employees shown include Thomas Schroecker.",
                ],
            },
            {
                "source_id": "linkedin_people_snapshot_20260409",
                "title": "LinkedIn people snapshot for Venuiti Solutions, DevStaff Canada, and Venuiti Healthcare",
                "url": "https://www.linkedin.com/",
                "source_type": "provided_linkedin_snapshot",
                "publisher": "LinkedIn",
                "domain": "linkedin.com",
                "snapshot_date": SNAPSHOT_DATE,
                "key_points": [
                    "Thomas Schroecker is described as CEO & Founder of Venuiti Group of Companies across Venuiti Healthcare, Venuiti Solutions, and DevStaff Canada.",
                    "Alexey Sidelnikov is described as CTO at Venuiti Group of Companies across Venuiti Solutions, Venuiti Healthcare, and DevStaff Canada.",
                    "Jordan Schroecker is described as Director of Operations @ Venuiti Group of Companies, DevStaff Canada & Venuiti Healthcare.",
                    "Additional public profiles indicate talent acquisition, operations, AI engineering, frontend development, and healthcare software delivery roles across the group.",
                ],
            },
        ],
    }
}
