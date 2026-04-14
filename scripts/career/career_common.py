from __future__ import annotations

import csv
import hashlib
import html
import json
import logging
import re
import traceback
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "career"
DOCS_DIR = ROOT / "docs"
REPORTS_DIR = ROOT / "reports"
PACKAGE_DIR = REPORTS_DIR / "packages"
PACKAGE_PATH = PACKAGE_DIR / "career_outputs_bundle.zip"
VALIDATION_SUMMARY_PATH = REPORTS_DIR / "data" / "career_validation_summary.json"

SOURCE_ROOTS = [
    Path(r"C:\Users\andrew\Documents\Job_Search"),
    Path(r"G:\My Drive\Files-Home\Job_Search++"),
]
CANONICAL_SOURCE_FILES = [
    Path(r"G:\My Drive\Files-Home\Job_Search++\Master Career Document (Data Source).docx"),
    Path(r"G:\My Drive\Files-Home\Job_Search++\Supporting Source Files(updated).docx"),
    Path(r"G:\My Drive\Files-Home\Job_Search++\Supporting Source Files.docx"),
    Path(r"G:\My Drive\Files-Home\Job_Search++\Reference - Work History and Education working table for online forms.xlsx"),
    Path(r"G:\My Drive\Files-Home\Job_Search++\Manual Summary of Career Timeline for Employer based Application Systems.docx"),
    Path(r"G:\My Drive\Files-Home\Job_Search++\Andrew.J.Pearen.baseline.docx"),
    Path(r"C:\Users\andrew\Documents\Job_Search\My Experence-Scope-Domains.docx"),
]
SUPPORTED_EXTENSIONS = {".csv", ".doc", ".docx", ".htm", ".html", ".json", ".md", ".pdf", ".txt", ".xlsx"}
CAREER_KEYWORDS = [
    "application",
    "baseline",
    "career",
    "cert",
    "compliance",
    "cv",
    "education",
    "employment",
    "erp",
    "experience",
    "forms",
    "history",
    "hris",
    "interview",
    "linkedin",
    "master",
    "payroll",
    "profile",
    "resume",
    "risk",
    "scope",
    "security",
    "source",
    "supporting",
    "timeline",
    "work history",
]
SOURCE_FOLDER_HINTS = {
    "baseline",
    "baselines",
    "certs and dips",
    "copy from computer",
    "load to chatgpt",
    "old resumes to upload",
    "reference files for chatgpt projects",
    "temp-collection-resumes",
    "transfers from g drive",
    "wip docs",
}
EXCLUDED_PATH_PARTS = {
    ".git",
    "__pycache__",
    "attachments",
    "backup",
    "downloads",
    "node_modules",
    "old.ssd_and_google.drive_files",
    "resources",
    "supporting_assets",
    "webcache",
}
PRIORITY_NAME_HINTS = [
    "andrew",
    "baseline",
    "career",
    "data source",
    "education",
    "experience",
    "history",
    "linkedin",
    "master",
    "resume",
    "scope",
    "source",
    "supporting",
    "timeline",
    "work history",
]
EVIDENCE_NAME_HINTS = [
    "andrew",
    "baseline",
    "blues",
    "career",
    "certificate",
    "certification",
    "cover letter",
    "data source",
    "education",
    "experience",
    "full listing",
    "governance",
    "history",
    "hris",
    "lawson",
    "linkedin",
    "manual summary",
    "master",
    "microtrek",
    "opentext",
    "payroll",
    "profile",
    "reference",
    "resume",
    "risk",
    "scope",
    "security_consultant",
    "source",
    "supporting",
    "timeline",
    "transcript",
    "work history",
    "working table",
]
NOISE_NAME_TOKENS = [
    "ai prompt",
    "application status",
    "assessment",
    "compare",
    "description-",
    "email-",
    "interview prep",
    "interview question",
    "job posting",
    "keyword",
    "notes-",
    "posating-",
    "posting-",
    "review your application",
    "salary",
    "upload-",
]
EMPLOYER_ALIASES = {
    "opentext": ["opentext", "open text"],
    "manulife_financial": ["manulife", "manulife financial"],
    "sun_life_financial": ["sun life", "sunlife"],
    "economical_insurance": ["economical insurance", "economical"],
    "spaenaur_inc": ["spaenaur"],
    "hubble_technology_consulting_inc": ["hubble technology consulting", "hubble"],
    "kuntz_electroplating_inc": ["kuntz electroplating", "kuntz"],
    "second_foundation_inc": ["second foundation"],
    "best_software": ["best software", "abra"],
    "microtrek_develop": ["microtrek"],
    "waterloo_chronicle": ["waterloo chronicle"],
    "aintree_hedge_trimmer": ["aintree hedge trimmer", "seasonal / outdoor maintenance"],
    "guest_speaking": ["fanshawe college", "fanshaw college", "conestoga college", "pmi"],
    "medshare": ["medshare"],
}
FRAMEWORK_PATTERNS = [
    "Archer", "AuditBoard", "CE+", "COBIT", "COSO", "CSAE3416", "Cyber Essentials Plus",
    "FedRAMP", "GDPR", "ISO 27001", "ITIL", "JIRA", "Lawson", "NIST", "OneTrust",
    "Onspring", "PCI", "Power BI", "Power Automate", "Power Query", "RSA Archer",
    "Sage", "ServiceNow", "SharePoint", "SOX", "SOC1", "SOC2",
]
STAKEHOLDER_PATTERNS = [
    "academic institutions", "auditors", "business leaders", "clients", "developers",
    "educational leaders", "engineers", "executives", "offshore teams", "onshore teams",
    "participants", "PMO", "procurement", "project team", "senior leadership", "stakeholders",
    "students", "technical team", "vendors",
]
INDUSTRY_PATTERNS = {
    "education": ["college", "students", "academic"],
    "financial_services": ["financial", "bank", "insurance", "benefits", "retirement"],
    "healthcare": ["healthcare", "health care", "hospital", "medshare"],
    "manufacturing": ["supplier", "electroplating", "manufacturing"],
    "non_profit": ["non-profit", "non profit"],
    "public_sector": ["public sector", "government"],
    "retail": ["retailer", "retail"],
    "software": ["software", "saas", "application", "erp"],
    "staffing": ["staffing", "recruit", "recruiter"],
}
CERTIFICATION_KEYWORDS = ["PMP", "ITIL", "CMMI", "CRM", "CRISC", "ISO", "CEH"]
AWKWARD_EMPLOYERS = {"medshare", "microtrek_develop"}


class CareerBuildError(RuntimeError):
    pass


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    VALIDATION_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_logger(log_name: str) -> logging.Logger:
    ensure_dirs()
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler = logging.FileHandler(DATA_DIR / log_name, encoding="utf-8")
    file_handler.setFormatter(formatter)
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def normalize_whitespace(value: str) -> str:
    value = html.unescape(value or "")
    return re.sub(r"\s+", " ", value).strip()


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower().strip()).strip("_") or "unknown"


def stable_hash(value: str, length: int = 12) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:length]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def run_logged(logger: logging.Logger, fn) -> int:
    try:
        fn()
        logger.info("completed successfully")
        return 0
    except Exception as exc:
        logger.error("failed: %s", exc)
        logger.error("%s", traceback.format_exc())
        return 1


def format_month_year(value: str) -> str | None:
    value = normalize_whitespace(value)
    if not value:
        return None
    if value.lower() == "present":
        return "Present"
    if re.fullmatch(r"\d{4}", value):
        return f"{value}-01"
    match = re.fullmatch(r"(\d{1,2})/(\d{4})", value)
    if match:
        month, year = match.groups()
        return f"{int(year):04d}-{int(month):02d}"
    if re.fullmatch(r"\d+(\.\d+)?", value):
        base = datetime(1899, 12, 30)
        parsed = base + timedelta(days=float(value))
        return f"{parsed.year:04d}-{parsed.month:02d}"
    for fmt in ("%b %Y", "%B %Y", "%Y-%m"):
        try:
            parsed = datetime.strptime(value, fmt)
            return f"{parsed.year:04d}-{parsed.month:02d}"
        except ValueError:
            continue
    return value


def months_between(start: str | None, end: str | None) -> int | None:
    if not start or not re.fullmatch(r"\d{4}-\d{2}", start):
        return None
    if end == "Present":
        end_dt = datetime.now()
    elif end and re.fullmatch(r"\d{4}-\d{2}", end):
        year, month = end.split("-")
        end_dt = datetime(int(year), int(month), 1)
    else:
        return None
    year, month = start.split("-")
    start_dt = datetime(int(year), int(month), 1)
    return (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month) + 1


def read_docx_text(path: Path) -> str:
    chunks: list[str] = []
    with ZipFile(path) as archive:
        names = sorted(name for name in archive.namelist() if name.startswith("word/") and name.endswith(".xml"))
        for name in names:
            raw = archive.read(name).decode("utf-8", errors="ignore")
            chunks.append(normalize_whitespace(re.sub(r"<[^>]+>", " ", raw)))
    return normalize_whitespace(" ".join(chunk for chunk in chunks if chunk))


def read_xlsx_rows(path: Path) -> dict[str, list[list[str]]]:
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    rel_ns = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    rows_by_sheet: dict[str, list[list[str]]] = {}
    with ZipFile(path) as archive:
        shared_strings: list[str] = []
        try:
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root:
                shared_strings.append(
                    normalize_whitespace("".join(node.text or "" for node in item.iter() if node.tag == f"{ns}t"))
                )
        except KeyError:
            pass
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}
        sheets = workbook.find(f"{ns}sheets")
        if sheets is None:
            return rows_by_sheet
        for sheet in sheets:
            name = sheet.attrib.get("name", "Sheet")
            rel_id = sheet.attrib.get(f"{rel_ns}id")
            if not rel_id:
                continue
            target = "xl/" + rel_map[rel_id].lstrip("/")
            worksheet = ET.fromstring(archive.read(target))
            parsed_rows: list[list[str]] = []
            for row in worksheet.iter(f"{ns}row"):
                cells: list[str] = []
                for cell in row.iter(f"{ns}c"):
                    cell_type = cell.attrib.get("t")
                    inline = cell.find(f"{ns}is")
                    if inline is not None:
                        cells.append(normalize_whitespace("".join(node.text or "" for node in inline.iter() if node.tag == f"{ns}t")))
                        continue
                    value = cell.find(f"{ns}v")
                    if value is None:
                        cells.append("")
                        continue
                    raw = value.text or ""
                    if cell_type == "s" and raw.isdigit():
                        idx = int(raw)
                        raw = shared_strings[idx] if idx < len(shared_strings) else raw
                    cells.append(normalize_whitespace(raw))
                parsed_rows.append(cells)
            rows_by_sheet[name] = parsed_rows
    return rows_by_sheet


def read_xlsx_text(path: Path) -> str:
    parts: list[str] = []
    for name, rows in read_xlsx_rows(path).items():
        parts.append(name)
        for row in rows:
            line = " | ".join(cell for cell in row if cell)
            if line:
                parts.append(line)
    return normalize_whitespace(" ".join(parts))


def read_html_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="ignore")
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    return normalize_whitespace(re.sub(r"<[^>]+>", " ", text))


def read_plain_text(path: Path) -> str:
    return normalize_whitespace(path.read_text(encoding="utf-8", errors="ignore"))


def read_csv_text(path: Path) -> str:
    parts: list[str] = []
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as handle:
        for row in csv.reader(handle):
            parts.append(" | ".join(normalize_whitespace(cell) for cell in row if cell))
    return normalize_whitespace(" ".join(parts))


def read_json_text(path: Path) -> str:
    return normalize_whitespace(json.dumps(json.loads(path.read_text(encoding="utf-8", errors="ignore")), sort_keys=True))


def read_pdf_text(path: Path) -> str:
    data = path.read_bytes()
    chunks = re.findall(rb"[A-Za-z0-9][A-Za-z0-9 ,./&()\-:+]{5,}", data)
    return normalize_whitespace(" ".join(chunk.decode("latin-1", errors="ignore") for chunk in chunks[:4000]))


def extract_text(path: Path) -> tuple[str, str, list[str]]:
    ext = path.suffix.lower()
    errors: list[str] = []
    try:
        if ext == ".docx":
            return read_docx_text(path), "supported", errors
        if ext == ".xlsx":
            return read_xlsx_text(path), "supported", errors
        if ext in {".html", ".htm"}:
            return read_html_text(path), "supported", errors
        if ext in {".txt", ".md"}:
            return read_plain_text(path), "supported", errors
        if ext == ".csv":
            return read_csv_text(path), "supported", errors
        if ext == ".json":
            return read_json_text(path), "supported", errors
        if ext == ".pdf":
            return read_pdf_text(path), "best_effort_pdf", errors
        if ext == ".doc":
            return "", "unsupported", ["legacy .doc parsing not supported with stdlib-only pipeline"]
    except Exception as exc:
        return "", "error", [str(exc)]
    return "", "unsupported", [f"unsupported extension: {ext}"]


def is_relevant_source(path: Path) -> bool:
    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        return False
    lowered_parts = [part.lower() for part in path.parts]
    if any(part in EXCLUDED_PATH_PARTS or part.endswith("_files") for part in lowered_parts):
        return False
    name = path.name.lower()
    parent_haystack = " ".join(lowered_parts[-4:])
    if path in CANONICAL_SOURCE_FILES:
        return True
    if "~$" in name:
        return False
    if any(token in name for token in NOISE_NAME_TOKENS):
        return False
    if "job posting" in parent_haystack and not any(hint in name for hint in ["resume", "career", "timeline", "work history", "supporting"]):
        return False
    if any(hint in name for hint in EVIDENCE_NAME_HINTS):
        return True
    if any(alias in name for aliases in EMPLOYER_ALIASES.values() for alias in aliases):
        return True
    if any(keyword in name for keyword in CAREER_KEYWORDS) and "resume" in name:
        return True
    if path.suffix.lower() in {".html", ".htm"}:
        return False
    return False


def discover_source_files(logger: logging.Logger) -> list[Path]:
    paths: set[Path] = set()
    for source in CANONICAL_SOURCE_FILES:
        if source.exists():
            paths.add(source)
    for root in SOURCE_ROOTS:
        if not root.exists():
            logger.warning("source root missing: %s", root)
            continue
        for path in root.rglob("*"):
            if path.is_file() and is_relevant_source(path):
                paths.add(path)
    ordered = sorted(paths, key=lambda item: str(item).lower())
    deduped: dict[str, Path] = {}
    for path in ordered:
        key = source_dedupe_key(path)
        current = deduped.get(key)
        if current is None or source_sort_key(path) < source_sort_key(current):
            deduped[key] = path
    final_paths = sorted(deduped.values(), key=lambda item: str(item).lower())
    logger.info("discovered %s candidate source files", len(final_paths))
    logger.info("deduplicated %s duplicate source candidates by normalized filename", len(ordered) - len(final_paths))
    return final_paths


def source_dedupe_key(path: Path) -> str:
    name = path.stem.lower()
    name = re.sub(r"\b(copy|draft|final|updated|autosaved|merged|compressed|test)\b", " ", name)
    name = re.sub(r"\(\d+\)", " ", name)
    name = re.sub(r"[-_.]+", " ", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name


def source_sort_key(path: Path) -> tuple[int, int, str]:
    ext_rank = {
        ".docx": 0,
        ".xlsx": 1,
        ".json": 2,
        ".txt": 3,
        ".csv": 4,
        ".pdf": 5,
        ".doc": 6,
        ".html": 7,
        ".htm": 8,
        ".md": 9,
    }
    return (ext_rank.get(path.suffix.lower(), 99), len(str(path)), str(path).lower())


def load_source_artifacts(logger: logging.Logger) -> list[dict[str, Any]]:
    artifacts: list[dict[str, Any]] = []
    for path in discover_source_files(logger):
        logger.info("extracting source: %s", path)
        text, status, errors = extract_text(path)
        artifacts.append(
            {
                "path": path,
                "relative_path": str(path),
                "extension": path.suffix.lower(),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "size_bytes": path.stat().st_size,
                "extraction_status": status,
                "text": text,
                "errors": errors,
            }
        )
    return artifacts


def detect_mentions(text: str) -> dict[str, int]:
    lowered = text.lower()
    mentions: dict[str, int] = {}
    for entity_id, aliases in EMPLOYER_ALIASES.items():
        count = sum(lowered.count(alias.lower()) for alias in aliases)
        if count:
            mentions[entity_id] = count
    return mentions


def top_keywords(text: str, limit: int = 12) -> list[str]:
    found: list[str] = []
    lowered = text.lower()
    for item in FRAMEWORK_PATTERNS + CERTIFICATION_KEYWORDS:
        if item.lower() in lowered and item not in found:
            found.append(item)
    return found[:limit]


def build_source_index(artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    entries = []
    for artifact in artifacts:
        snippets = []
        if artifact["text"]:
            for part in re.split(r"(?<=[.!?])\s+", artifact["text"]):
                normalized = normalize_whitespace(part)
                if normalized and len(normalized) > 40:
                    snippets.append(normalized[:280])
                if len(snippets) == 5:
                    break
        entries.append(
            {
                "source_id": f"src_{stable_hash(artifact['relative_path'].lower())}",
                "path": artifact["relative_path"],
                "extension": artifact["extension"],
                "size_bytes": artifact["size_bytes"],
                "sha256": artifact["sha256"],
                "extraction_status": artifact["extraction_status"],
                "errors": artifact["errors"],
                "mentioned_entities": detect_mentions(artifact["text"]),
                "detected_keywords": top_keywords(artifact["text"]),
                "snippets": snippets,
            }
        )
    return {
        "schema_version": "1.0",
        "source_policy": {
            "treatment": "Historical resumes and related documents are evidence inputs only, not final truth.",
            "normalization_rule": "Equivalent facts are merged while duplicate source references are preserved.",
            "omission_rule": "Omission from recent resumes is not treated as negative evidence.",
        },
        "deduplication_notes": {
            "strict_rule": "Repetition across job-specific resume variants is not counted as signal strength.",
            "included_source_count": len(entries),
            "excluded_noise_examples": [
                "job posting text",
                "recruiter summaries",
                "ATS-only keyword packs",
                "cover-letter-only files",
            ],
        },
        "sources": entries,
    }


def make_source_reference(path: Path | str, excerpt: str, confidence_boost: int = 0) -> dict[str, Any]:
    path_str = str(path)
    return {
        "source_id": f"src_{stable_hash(path_str.lower())}",
        "path": path_str,
        "excerpt": excerpt[:320],
        "confidence_boost": confidence_boost,
    }


def confidence_payload(source_count: int, evidence_type: str) -> dict[str, Any]:
    base = 0.35
    if evidence_type == "xlsx_workbook":
        base = 0.8
    elif evidence_type == "docx_master":
        base = 0.65
    elif evidence_type == "inferred":
        base = 0.45
    score = min(0.98, round(base + min(source_count, 5) * 0.04, 2))
    label = "high" if score >= 0.85 else "medium" if score >= 0.65 else "low"
    return {"label": label, "score": score}


def split_bullets(text: str) -> list[str]:
    text = (text or "").replace("•", "\n•")
    items = []
    for chunk in re.split(r"\n|(?<=\.)\s+(?=[A-Z])", text):
        normalized = normalize_whitespace(chunk.lstrip("•-"))
        if normalized and len(normalized) > 15:
            items.append(normalized)
    return items


def extract_metrics(text: str) -> list[str]:
    found = []
    for metric in re.findall(r"(?:~?\$?\d+[A-Za-z+%/.-]*|\d+\s*[xX])", text or ""):
        cleaned = normalize_whitespace(metric)
        if cleaned and cleaned not in found:
            found.append(cleaned)
    return found[:12]


def extract_named_patterns(text: str, patterns: list[str]) -> list[str]:
    lowered = (text or "").lower()
    return [pattern for pattern in patterns if pattern.lower() in lowered]


def derive_relevance_tags(title: str, description: str) -> list[str]:
    haystack = f"{title} {description}".lower()
    checks = {
        "audit_controls": ["audit", "controls", "assurance"],
        "client_delivery": ["client", "delivery", "liaison"],
        "consulting": ["consultant", "consulting"],
        "cybersecurity": ["security", "cyber", "infosec"],
        "education_enablement": ["speaker", "training", "workshop", "present"],
        "erp": ["erp", "lawson", "epicor", "great plains", "sage"],
        "grc": ["risk", "compliance", "governance", "grc"],
        "hris_payroll": ["hris", "payroll", "hr/pay", "human resources"],
        "leadership": ["manager", "director", "lead"],
        "vendor_risk": ["vendor", "third-party", "third party"],
    }
    return [tag for tag, needles in checks.items() if any(needle in haystack for needle in needles)]


def infer_domains(title: str, description: str) -> list[str]:
    haystack = f"{title} {description}".lower()
    mapping = {
        "client_delivery": ["client", "delivery", "liaison"],
        "compliance": ["compliance", "regulatory"],
        "consulting": ["consultant", "consulting"],
        "erp": ["erp", "lawson", "epicor", "great plains", "sage"],
        "grc": ["grc", "governance", "risk", "compliance"],
        "leadership": ["manager", "director", "lead"],
        "pm": ["project", "program", "portfolio", "delivery"],
        "security": ["security", "cyber", "infosec"],
        "training": ["training", "workshop", "speaker", "present"],
    }
    return [label for label, needles in mapping.items() if any(needle in haystack for needle in needles)]


def infer_capability_tags(title: str, description: str) -> list[str]:
    haystack = f"{title} {description}".lower()
    mapping = {
        "audit": ["audit", "assurance"],
        "client_training": ["training", "speaker", "present"],
        "implementation": ["implement", "deployment", "delivery"],
        "iso27001_27017": ["iso 27001", "iso 27017", "cyber essentials plus", "ce+"],
        "program_delivery": ["project", "program", "portfolio", "pmo"],
        "sox_soc": ["sox", "soc1", "soc2", "csae3416"],
        "stakeholder_engagement": ["stakeholder", "executive", "leadership", "business leaders"],
        "third_party_risk": ["third-party", "third party", "vendor", "supplier"],
        "vendor_management": ["vendor", "contract", "procurement"],
    }
    return [label for label, needles in mapping.items() if any(needle in haystack for needle in needles)]


def default_visibility(role: dict[str, Any], employer_key: str, relevance_tags: list[str]) -> dict[str, Any]:
    months = months_between(role.get("start_date"), role.get("end_date"))
    hidden = employer_key in AWKWARD_EMPLOYERS or role.get("employment_type") == "seasonal" or (months is not None and months <= 9)
    allowed = sorted(set(relevance_tags + ["master_archive_review"]))
    notes = []
    suppression_reason = "none"
    if employer_key in AWKWARD_EMPLOYERS:
        notes.append("Historically relevant but potentially awkward employer; preserve for evidence and selective use only.")
        suppression_reason = "awkward_or_selective_employer"
    if months is not None and months <= 9:
        notes.append("Short tenure may create disproportionate screening focus if surfaced without role-fit justification.")
        suppression_reason = "short_tenure" if suppression_reason == "none" else suppression_reason
    if role.get("employment_type") == "seasonal":
        notes.append("Seasonal work is retained as truthful evidence but hidden outside directly relevant conversations.")
        suppression_reason = "seasonal_or_noncore_role" if suppression_reason == "none" else suppression_reason
    if not notes:
        notes.append("Visible by default because the record materially supports the core chronology.")
    return {
        "visibility_default": "hidden" if hidden else "visible",
        "visibility_allowed_for_target_roles": allowed,
        "inclusion_risk_note": " ".join(notes),
        "suppression_reason": suppression_reason,
        "relevance_tags": allowed,
    }


def canonical_employer_key(company: str) -> str:
    lowered = normalize_whitespace(company).lower()
    for key, aliases in EMPLOYER_ALIASES.items():
        if any(alias.lower() in lowered for alias in aliases):
            return key
    return slugify(lowered)


def clean_company_name(company: str) -> str:
    return normalize_whitespace(re.sub(r"\s*\([^)]*\)\s*", " ", normalize_whitespace(company)))


def infer_industries(company: str, description: str) -> list[str]:
    lowered = f"{company} {description}".lower()
    return [label for label, needles in INDUSTRY_PATTERNS.items() if any(needle in lowered for needle in needles)]


def parse_online_forms_workbook(artifacts: list[dict[str, Any]], logger: logging.Logger) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    workbook = next((artifact for artifact in artifacts if artifact["path"].name == "Reference - Work History and Education working table for online forms.xlsx"), None)
    if workbook is None:
        raise CareerBuildError("online forms workbook not found in discovered sources")
    roles: list[dict[str, Any]] = []
    education: list[dict[str, Any]] = []
    for rows in read_xlsx_rows(workbook["path"]).values():
        field_rows: dict[str, list[str]] = {}
        for row in rows:
            if row:
                label = normalize_whitespace(row[0])
                if label in {
                    "Job Title*", "Company*", "Location", "I currently work here", "From*", "To*", "Role Description",
                    "School or University*", "Degree*", "Field of Study", "Overall Result (GPA)", "From", "To (Actual or Expected)",
                }:
                    field_rows[label] = row[1:]
        if "Job Title*" in field_rows and "Company*" in field_rows:
            titles = field_rows["Job Title*"]
            companies = field_rows["Company*"]
            for index in range(min(len(titles), len(companies))):
                title = normalize_whitespace(titles[index])
                company = normalize_whitespace(companies[index])
                if not title or not company:
                    continue
                combined = f"{title} {company}".lower()
                if "#ref!" in combined or "please update" in combined:
                    continue
                location = normalize_whitespace(field_rows.get("Location", [""] * 99)[index])
                start = normalize_whitespace(field_rows.get("From*", [""] * 99)[index])
                end = normalize_whitespace(field_rows.get("To*", [""] * 99)[index])
                current = normalize_whitespace(field_rows.get("I currently work here", [""] * 99)[index])
                description = normalize_whitespace(field_rows.get("Role Description", [""] * 99)[index])
                roles.append(
                    {
                        "title": title,
                        "company": company,
                        "location": location,
                        "start_date": format_month_year(start),
                        "end_date": "Present" if current.lower() == "yes" else format_month_year(end),
                        "description": description,
                        "source_file": str(workbook["path"]),
                    }
                )
        if "School or University*" in field_rows and "Degree*" in field_rows:
            schools = field_rows["School or University*"]
            degrees = field_rows["Degree*"]
            for index in range(min(len(schools), len(degrees))):
                school = normalize_whitespace(schools[index])
                degree = normalize_whitespace(degrees[index])
                if not school or not degree:
                    continue
                education.append(
                    {
                        "education_id": f"edu_{slugify(school)}_{slugify(degree)}",
                        "institution": school,
                        "degree": degree,
                        "field_of_study": normalize_whitespace(field_rows.get("Field of Study", [""] * 99)[index]),
                        "result": normalize_whitespace(field_rows.get("Overall Result (GPA)", [""] * 99)[index]),
                        "start_date": format_month_year(normalize_whitespace(field_rows.get("From", [""] * 99)[index])),
                        "end_date": format_month_year(normalize_whitespace(field_rows.get("To (Actual or Expected)", [""] * 99)[index])),
                        "source_references": [make_source_reference(workbook["path"], "Structured education table entry", confidence_boost=2)],
                        "evidence_confidence": confidence_payload(2, "xlsx_workbook"),
                    }
                )
    deduped_roles: dict[str, dict[str, Any]] = {}
    for role in roles:
        key = "|".join(
            [
                canonical_employer_key(role["company"]),
                slugify(role["title"]),
                role.get("start_date") or "",
                role.get("end_date") or "",
            ]
        )
        start = role.get("start_date")
        end = role.get("end_date")
        if start and end and start != "Present" and end != "Present" and start > end:
            logger.info("dedupe filter dropped invalid role chronology: %s | %s | %s -> %s", role["title"], role["company"], start, end)
            continue
        current = deduped_roles.get(key)
        if current is None or len(role["description"]) > len(current["description"]):
            deduped_roles[key] = role
    canonical_roles: dict[str, dict[str, Any]] = {}
    for role in deduped_roles.values():
        key = "|".join([canonical_employer_key(role["company"]), slugify(role["title"])])
        current = canonical_roles.get(key)
        if current is None:
            canonical_roles[key] = role
            continue
        current_start = current.get("start_date") or ""
        role_start = role.get("start_date") or ""
        current_end = current.get("end_date") or ""
        role_end = role.get("end_date") or ""
        if role_end == "Present" and current_end == "Present":
            if role_start and (not current_start or role_start < current_start):
                canonical_roles[key] = role
        elif role_start and (not current_start or role_start > current_start):
            canonical_roles[key] = role
    deduped_education: dict[str, dict[str, Any]] = {}
    for item in education:
        deduped_education[item["education_id"]] = item
    logger.info("parsed %s role rows and %s education rows from workbook", len(canonical_roles), len(deduped_education))
    return list(canonical_roles.values()), list(deduped_education.values())


def infer_supplemental_roles(artifacts: list[dict[str, Any]], logger: logging.Logger) -> list[dict[str, Any]]:
    combined = " ".join(
        artifact["text"]
        for artifact in artifacts
        if artifact["path"].name in {
            "Master Career Document (Data Source).docx",
            "Supporting Source Files(updated).docx",
            "Supporting Source Files.docx",
        }
    )
    supplements: list[dict[str, Any]] = []
    fixed = [
        (
            "Office and Distribution Manager",
            "Waterloo Chronicle",
            "1993",
            "1996",
            "Led distribution teams, handled operational duties, and supervised staff in a local publishing environment.",
            "historical",
        ),
        (
            "Grounds Maintenance / Seasonal Outdoor Maintenance",
            "Aintree Hedge Trimmer",
            "",
            "",
            "Performed hedge trimming, turf repair, field preparation, and weekend animal care as seasonal maintenance work.",
            "seasonal",
        ),
    ]
    for title, company, start, end, description, employment_type in fixed:
        if company.lower() in combined.lower():
            path = next(
                artifact["path"]
                for artifact in artifacts
                if artifact["path"].name in {"Master Career Document (Data Source).docx", "Supporting Source Files(updated).docx", "Supporting Source Files.docx"}
                and company.lower() in artifact["text"].lower()
            )
            supplements.append(
                {
                    "title": title,
                    "company": company,
                    "start_date": format_month_year(start),
                    "end_date": format_month_year(end),
                    "description": description,
                    "employment_type": employment_type,
                    "evidence_type": "docx_master",
                    "source_references": [make_source_reference(path, description, confidence_boost=1)],
                }
            )
    if "medshare" in combined.lower():
        path = next(artifact["path"] for artifact in artifacts if "medshare" in artifact["text"].lower())
        supplements.append(
            {
                "title": "Historical role pending normalization",
                "company": "Medshare",
                "start_date": None,
                "end_date": None,
                "description": "Employer mention detected in historical evidence; retain hidden-by-default until chronology and title are recovered from stronger evidence.",
                "employment_type": "historical",
                "evidence_type": "inferred",
                "source_references": [make_source_reference(path, "Employer mention detected without a fully recoverable role block.", confidence_boost=0)],
            }
        )
    logger.info("inferred %s supplemental roles", len(supplements))
    return supplements


def infer_certifications(artifacts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: dict[str, dict[str, Any]] = {}
    for artifact in artifacts:
        for cert in CERTIFICATION_KEYWORDS:
            if cert.lower() in artifact["text"].lower():
                cert_id = f"cert_{slugify(cert)}"
                seen.setdefault(
                    cert_id,
                    {
                        "certification_id": cert_id,
                        "name": cert,
                        "source_references": [],
                        "evidence_confidence": confidence_payload(1, "docx_master"),
                    },
                )
                seen[cert_id]["source_references"].append(make_source_reference(artifact["path"], f"Detected certification keyword: {cert}", confidence_boost=1))
                seen[cert_id]["evidence_confidence"] = confidence_payload(len(seen[cert_id]["source_references"]), "docx_master")
    return sorted(seen.values(), key=lambda item: item["name"].lower())


def build_career_master_payload(artifacts: list[dict[str, Any]], logger: logging.Logger) -> dict[str, Any]:
    role_rows, education = parse_online_forms_workbook(artifacts, logger)
    employers: dict[str, dict[str, Any]] = {}
    roles: list[dict[str, Any]] = []
    for row in role_rows:
        employer_key = canonical_employer_key(row["company"])
        normalized_company = clean_company_name(row["company"])
        bullets = split_bullets(row["description"])
        tools = extract_named_patterns(row["description"], FRAMEWORK_PATTERNS)
        frameworks = [item for item in tools if item in {"CE+", "COBIT", "COSO", "CSAE3416", "FedRAMP", "GDPR", "ISO 27001", "NIST", "PCI", "SOX", "SOC1", "SOC2"}]
        stakeholders = extract_named_patterns(row["description"], STAKEHOLDER_PATTERNS)
        metrics = extract_metrics(row["description"])
        relevance_tags = derive_relevance_tags(row["title"], row["description"])
        domains = infer_domains(row["title"], row["description"])
        capability_tags = infer_capability_tags(row["title"], row["description"])
        visibility = default_visibility(row, employer_key, relevance_tags)
        refs = [make_source_reference(row["source_file"], row["description"][:280], confidence_boost=2)]
        for artifact in artifacts:
            mentions = detect_mentions(artifact["text"])
            if employer_key in mentions:
                match = re.search(rf"(.{{0,150}}{re.escape(normalized_company.split()[0])}.{{0,150}})", artifact["text"], flags=re.IGNORECASE)
                refs.append(make_source_reference(artifact["path"], normalize_whitespace(match.group(1)) if match else artifact["text"][:240], confidence_boost=1))
        role_id = f"role_{stable_hash(f'{employer_key}:{slugify(row['title'])}:{row.get('start_date') or 'unknown'}')}"
        role_payload = {
            "role_id": role_id,
            "employer_id": f"emp_{employer_key}",
            "title": row["title"],
            "dates": {"start": row["start_date"], "end": row["end_date"]},
            "location": row["location"],
            "tools": tools,
            "frameworks": frameworks,
            "responsibilities": bullets[:8],
            "achievements": [item for item in bullets if any(metric in item for metric in metrics)][:8],
            "metrics": metrics,
            "stakeholders": stakeholders,
            "domains": domains,
            "industries": infer_industries(normalized_company, row["description"]),
            "capability_tags": capability_tags,
            "customer_facing_indicators": {
                "is_customer_facing": any(tag in relevance_tags for tag in ["client_delivery", "consulting", "education_enablement"]),
                "signals": [tag for tag in relevance_tags if tag in {"client_delivery", "consulting", "education_enablement"}],
            },
            "source_references": refs,
            "evidence_confidence": confidence_payload(len(refs), "xlsx_workbook"),
            **visibility,
        }
        roles.append(role_payload)
        employer = employers.setdefault(
            employer_key,
            {
                "employer_id": f"emp_{employer_key}",
                "employer_name": normalized_company,
                "display_name": normalize_whitespace(row["company"]),
                "location": row["location"],
                "industries": [],
                "domains": [],
                "capability_tags": [],
                "tools": [],
                "frameworks": [],
                "roles": [],
                "source_references": [],
                "customer_facing_indicators": {"is_customer_facing": False, "signals": []},
                **visibility,
            },
        )
        employer["industries"] = sorted(set(employer["industries"]) | set(role_payload["industries"]))
        employer["domains"] = sorted(set(employer["domains"]) | set(domains))
        employer["capability_tags"] = sorted(set(employer["capability_tags"]) | set(capability_tags))
        employer["tools"] = sorted(set(employer["tools"]) | set(tools))
        employer["frameworks"] = sorted(set(employer["frameworks"]) | set(frameworks))
        employer["roles"].append(role_id)
        employer["source_references"].extend(refs)
        employer["customer_facing_indicators"]["is_customer_facing"] = employer["customer_facing_indicators"]["is_customer_facing"] or role_payload["customer_facing_indicators"]["is_customer_facing"]
        employer["customer_facing_indicators"]["signals"] = sorted(set(employer["customer_facing_indicators"]["signals"]) | set(role_payload["customer_facing_indicators"]["signals"]))

    for row in infer_supplemental_roles(artifacts, logger):
        employer_key = canonical_employer_key(row["company"])
        relevance_tags = derive_relevance_tags(row["title"], row["description"])
        domains = infer_domains(row["title"], row["description"])
        capability_tags = infer_capability_tags(row["title"], row["description"])
        visibility = default_visibility(row, employer_key, relevance_tags)
        role_id = f"role_{stable_hash(f'{employer_key}:{slugify(row['title'])}:{row.get('start_date') or 'unknown'}')}"
        if any(existing["role_id"] == role_id for existing in roles):
            continue
        role_payload = {
            "role_id": role_id,
            "employer_id": f"emp_{employer_key}",
            "title": row["title"],
            "dates": {"start": row.get("start_date"), "end": row.get("end_date")},
            "location": row.get("location", ""),
            "tools": extract_named_patterns(row["description"], FRAMEWORK_PATTERNS),
            "frameworks": extract_named_patterns(row["description"], FRAMEWORK_PATTERNS),
            "responsibilities": split_bullets(row["description"])[:8],
            "achievements": split_bullets(row["description"])[:4],
            "metrics": extract_metrics(row["description"]),
            "stakeholders": extract_named_patterns(row["description"], STAKEHOLDER_PATTERNS),
            "domains": domains,
            "industries": infer_industries(row["company"], row["description"]),
            "capability_tags": capability_tags,
            "customer_facing_indicators": {
                "is_customer_facing": any(tag in relevance_tags for tag in ["client_delivery", "consulting"]),
                "signals": [tag for tag in relevance_tags if tag in {"client_delivery", "consulting"}],
            },
            "source_references": row["source_references"],
            "evidence_confidence": confidence_payload(len(row["source_references"]), row["evidence_type"]),
            **visibility,
        }
        roles.append(role_payload)
        employers.setdefault(
            employer_key,
            {
                "employer_id": f"emp_{employer_key}",
                "employer_name": clean_company_name(row["company"]),
                "display_name": row["company"],
                "location": row.get("location", ""),
                "industries": role_payload["industries"],
                "domains": domains,
                "capability_tags": capability_tags,
                "tools": role_payload["tools"],
                "frameworks": role_payload["frameworks"],
                "roles": [role_id],
                "source_references": list(row["source_references"]),
                "customer_facing_indicators": role_payload["customer_facing_indicators"],
                **visibility,
            },
        )
        if role_id not in employers[employer_key]["roles"]:
            employers[employer_key]["roles"].append(role_id)
    return {
        "schema_version": "1.0",
        "design_rule": {
            "career_master_json": "Master fact warehouse for cross-role, cross-company evidence.",
            "story_master_json": "Reusable story warehouse generated from the master fact warehouse.",
        },
        "profile": {
            "name": "Andrew J. Pearen",
            "summary": "Cross-era career warehouse built from historical evidence inputs with traceability and selective visibility controls.",
            "source_roots": [str(path) for path in SOURCE_ROOTS],
        },
        "employers": sorted(employers.values(), key=lambda item: (item["display_name"].lower(), item["employer_id"])),
        "roles": sorted(roles, key=lambda item: (item["dates"]["start"] or "9999-99", item["title"].lower())),
        "certifications": infer_certifications(artifacts),
        "education": sorted(education, key=lambda item: (item.get("start_date") or "9999-99", item["institution"].lower())),
    }


def build_entity_timeline(career_master: dict[str, Any]) -> dict[str, Any]:
    employers = {item["employer_id"]: item for item in career_master["employers"]}
    events: list[dict[str, Any]] = []
    for role in career_master["roles"]:
        employer = employers.get(role["employer_id"], {})
        events.append(
            {
                "entity_type": "role",
                "entity_id": role["role_id"],
                "label": role["title"],
                "organization": employer.get("display_name", ""),
                "start_date": role["dates"]["start"],
                "end_date": role["dates"]["end"],
                "sort_date": role["dates"]["start"] or "9999-99",
                "visibility_default": role["visibility_default"],
                "evidence_confidence": role["evidence_confidence"],
                "source_references": role["source_references"],
            }
        )
    for education in career_master["education"]:
        events.append(
            {
                "entity_type": "education",
                "entity_id": education["education_id"],
                "label": education["degree"],
                "organization": education["institution"],
                "start_date": education["start_date"],
                "end_date": education["end_date"],
                "sort_date": education["start_date"] or education["end_date"] or "9999-99",
                "visibility_default": "visible",
                "evidence_confidence": education["evidence_confidence"],
                "source_references": education["source_references"],
            }
        )
    for cert in career_master["certifications"]:
        events.append(
            {
                "entity_type": "certification",
                "entity_id": cert["certification_id"],
                "label": cert["name"],
                "organization": "",
                "start_date": None,
                "end_date": None,
                "sort_date": "9999-99",
                "visibility_default": "visible",
                "evidence_confidence": cert["evidence_confidence"],
                "source_references": cert["source_references"],
            }
        )
    events.sort(key=lambda item: (item["sort_date"], item["entity_type"], item["label"].lower()))
    return {"schema_version": "1.0", "events": events}


def write_html(path: Path, title: str, body: str) -> None:
    path.write_text(
        "\n".join(
            [
                "<!DOCTYPE html>",
                '<html lang="en">',
                "<head>",
                '  <meta charset="utf-8">',
                '  <meta name="viewport" content="width=device-width, initial-scale=1">',
                f"  <title>{html.escape(title)}</title>",
                '  <link rel="stylesheet" href="../app/assets/css/app.css">',
                "</head>",
                "<body>",
                '  <main class="shell">',
                '    <section class="hero">',
                '      <div class="breadcrumbs"><a href="index.html">Docs</a> / Career Warehouse</div>',
                f"      <h1>{html.escape(title)}</h1>",
                "    </section>",
                f'    <section class="section">{body}</section>',
                "  </main>",
                "</body>",
                "</html>",
                "",
            ]
        ),
        encoding="utf-8",
    )


def create_docs(career_master: dict[str, Any], source_index: dict[str, Any]) -> None:
    employer_count = len(career_master["employers"])
    role_count = len(career_master["roles"])
    hidden_roles = sum(1 for role in career_master["roles"] if role["visibility_default"] == "hidden")
    source_count = len(source_index["sources"])
    write_html(
        DOCS_DIR / "career_master_design.html",
        "Career Master Design",
        (
            f"<p><code>career_master.json</code> is the warehouse of normalized facts across {employer_count} employers and {role_count} roles.</p>"
            "<ul class=\"doc-list\">"
            "<li>Structured workbook rows are treated as high-confidence chronology anchors.</li>"
            "<li>Historical resumes and source documents enrich tools, frameworks, achievements, and duplicate evidence traces.</li>"
            f"<li>{hidden_roles} role records are hidden by default because they are short-tenure, awkward, seasonal, or selectively relevant.</li>"
            "<li>Duplicate source evidence is preserved inside each role and employer record instead of collapsed away.</li>"
            "</ul>"
        ),
    )
    write_html(
        DOCS_DIR / "story_master_design.html",
        "Story Master Design",
        (
            "<p><code>story_master.json</code> is generated from the fact warehouse and stores reusable interview stories that are not company-specific.</p>"
            "<ul class=\"doc-list\">"
            "<li>Stable story IDs are derived from normalized role and theme slugs.</li>"
            "<li>Each story retains source roles, employers, role-fit tags, audience-fit guidance, and sensitivity flags.</li>"
            "<li>Preferred/avoid guidance is intended for downstream tailoring, not public surfacing.</li>"
            "</ul>"
        ),
    )
    write_html(
        DOCS_DIR / "career_parsing_runbook.html",
        "Career Parsing Runbook",
        (
            f"<p>The current run ingests {source_count} source artifacts from the configured historical job-search roots and writes whole-file outputs under <code>data/career/</code>.</p>"
            "<ol class=\"doc-list\">"
            "<li>Discover supported career-relevant files recursively from the configured source roots.</li>"
            "<li>Extract text deterministically from DOCX/XLSX/HTML/TXT/CSV/JSON and best-effort PDF content.</li>"
            "<li>Use the online-forms workbook as the canonical role and education spine.</li>"
            "<li>Enrich facts from supporting documents while preserving every source reference.</li>"
            "<li>Activate downstream Venuiti opportunity files through alias resolution to canonical master-story IDs.</li>"
            "<li>Validate JSON structure, story references, downstream activation state, and Python compilation for all <code>scripts/career/*.py</code> files.</li>"
            "<li>Generate the career master, story master, source index, entity timeline, activation summary, validation summary, logs, and zip bundle.</li>"
            "</ol>"
            "<p>Operational command: <code>python scripts/career/run_career_pipeline.py</code>.</p>"
        ),
    )


def create_zip_bundle(logger: logging.Logger, required_paths: list[Path]) -> None:
    PACKAGE_DIR.mkdir(parents=True, exist_ok=True)
    with ZipFile(PACKAGE_PATH, "w") as archive:
        for path in sorted(required_paths, key=lambda item: str(item).lower()):
            info = ZipInfo(path.relative_to(ROOT).as_posix())
            info.date_time = (2026, 1, 1, 0, 0, 0)
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, path.read_bytes())
            logger.info("packaged %s", path.relative_to(ROOT).as_posix())
