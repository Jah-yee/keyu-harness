"""Validate source, claim, and artifact ledgers without changing source records."""
from pathlib import Path
import csv
import re

SOURCE_FIELDS = {
    "source_id", "title", "source_type", "source_role", "url",
    "review_status", "capture_status", "what_it_supports", "limits"
}
CLAIM_FIELDS = {
    "claim_id", "claim", "source_ids", "support_relation", "status",
    "direct_support", "limitations", "missing_evidence", "next_action"
}
ARTIFACT_FIELDS = {
    "artifact_id", "project", "artifact_kind", "public_identifier", "source_ids",
    "version_or_revision", "observed_metadata", "acquisition_status",
    "sha256", "local_path", "producer", "consumer", "limits"
}
ALLOWED_SOURCE_ROLES = {
    "INCIDENT_MATERIALS_PAGE", "SECONDARY_REPORT", "STATEMENT_REPRINT", "PUBLIC_SOFTWARE_REPOSITORY",
    "RESEARCH_PAPER", "PUBLIC_MODEL_CONFIG", "VERSION_REFERENCE",
    "SOFTWARE_CITATION_GUIDANCE", "RESEARCH_REPRODUCIBILITY_GUIDANCE",
    "TECHNICAL_REFERENCE"
}
ALLOWED_REVIEW_STATUSES = {"NOT_REVIEWED", "PAGE_REVIEWED", "PARTIALLY_REVIEWED", "NEEDS_REVIEW"}
ALLOWED_CAPTURE_STATUSES = {"LINK_ONLY", "REVISION_IDENTIFIED", "CAPTURED", "HASHED", "ARCHIVED"}
ALLOWED_CLAIM_STATUSES = {
    "DIRECTLY_SUPPORTED", "DIRECTLY_SUPPORTED_WITH_SCOPE_LIMIT",
    "DIRECTLY_SUPPORTED_FOR_THIS_CONFIG_REVISION", "CORROBORATED",
    "REPORTED_NOT_INDEPENDENTLY_VERIFIED", "INFERRED", "UNRESOLVED",
    "CONTRADICTED", "SIMULATED"
}
ALLOWED_SUPPORT_RELATIONS = {
    "DIRECT", "REPORTED_BY_SOURCE", "MIXED_CONTEXT", "INDIRECT",
    "INSUFFICIENT", "NOT_ESTABLISHED", "NOT_APPLICABLE"
}
ALLOWED_ARTIFACT_STATUSES = {
    "REFERENCED_NOT_CAPTURED", "REVISION_IDENTIFIED", "NOT_OBTAINED",
    "CAPTURED", "HASHED", "ARCHIVED"
}
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")

def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        return list(reader), set(reader.fieldnames or [])

def validate_csv(path: Path, required_fields: set[str]):
    errors = []
    try:
        rows, fields = read_csv(path)
    except (OSError, UnicodeError, csv.Error) as exc:
        return [f"Unable to read CSV: {exc}"]

    missing = required_fields - fields
    if missing:
        errors.append(f"Missing required columns: {', '.join(sorted(missing))}")
        return errors

    id_field = ("source_id" if "source_id" in required_fields else
                    "claim_id" if "claim_id" in required_fields else "artifact_id")
    seen = set()
    for line_no, row in enumerate(rows, start=2):
        record_id = (row.get(id_field) or "").strip()
        if not record_id:
            errors.append(f"Line {line_no}: empty {id_field}")
        elif record_id in seen:
            errors.append(f"Line {line_no}: duplicate {id_field} {record_id}")
        seen.add(record_id)

        if "url" in required_fields:
            url = (row.get("url") or "").strip()
            if url and not url.startswith(("https://", "http://")):
                errors.append(f"Line {line_no}: URL must use http(s)")
            if not url and row.get("source_role") not in {"INCIDENT_MATERIALS_PAGE"}:
                errors.append(f"Line {line_no}: missing URL for a public source")

        if "source_role" in required_fields:
            role = (row.get("source_role") or "").strip()
            if role not in ALLOWED_SOURCE_ROLES:
                errors.append(f"Line {line_no}: unknown source_role {role}")

        if "review_status" in required_fields:
            status = (row.get("review_status") or "").strip()
            if status not in ALLOWED_REVIEW_STATUSES:
                errors.append(f"Line {line_no}: unknown review_status {status}")

        if "capture_status" in required_fields:
            status = (row.get("capture_status") or "").strip()
            if status not in ALLOWED_CAPTURE_STATUSES:
                errors.append(f"Line {line_no}: unknown capture_status {status}")
            local_path = (row.get("local_path") or "").strip()
            digest = (row.get("sha256") or "").strip()
            if status in {"CAPTURED", "HASHED", "ARCHIVED"} and not local_path:
                errors.append(f"Line {line_no}: {status} requires local_path")
            if status in {"HASHED", "ARCHIVED"} and not SHA256_RE.fullmatch(digest):
                errors.append(f"Line {line_no}: {status} requires a 64-character SHA-256")
            if status == "REVISION_IDENTIFIED" and not ((row.get("version_or_commit") or row.get("version_or_revision") or "").strip()):
                errors.append(f"Line {line_no}: REVISION_IDENTIFIED requires version_or_commit/version_or_revision")
            if status == "LINK_ONLY" and (local_path or digest):
                errors.append(f"Line {line_no}: LINK_ONLY must not claim a local path or hash")

        if "status" in required_fields and "support_relation" in required_fields:
            status = (row.get("status") or "").strip()
            relation = (row.get("support_relation") or "").strip()
            if status not in ALLOWED_CLAIM_STATUSES:
                errors.append(f"Line {line_no}: unknown claim status {status}")
            if relation not in ALLOWED_SUPPORT_RELATIONS:
                errors.append(f"Line {line_no}: unknown support_relation {relation}")
            if status == "SIMULATED" and relation != "NOT_APPLICABLE":
                errors.append(f"Line {line_no}: SIMULATED claim must use NOT_APPLICABLE support relation")

        if "artifact_id" in required_fields:
            status = (row.get("acquisition_status") or "").strip()
            if status not in ALLOWED_ARTIFACT_STATUSES:
                errors.append(f"Line {line_no}: unknown acquisition_status {status}")
            local_path = (row.get("local_path") or "").strip()
            digest = (row.get("sha256") or "").strip()
            if status in {"CAPTURED", "HASHED", "ARCHIVED"} and not local_path:
                errors.append(f"Line {line_no}: {status} requires local_path")
            if status in {"HASHED", "ARCHIVED"} and not SHA256_RE.fullmatch(digest):
                errors.append(f"Line {line_no}: {status} requires a 64-character SHA-256")
            if status == "REVISION_IDENTIFIED" and not ((row.get("version_or_commit") or row.get("version_or_revision") or "").strip()):
                errors.append(f"Line {line_no}: REVISION_IDENTIFIED requires version_or_commit/version_or_revision")
            if status in {"REFERENCED_NOT_CAPTURED", "NOT_OBTAINED", "REVISION_IDENTIFIED"} and (local_path or digest):
                errors.append(f"Line {line_no}: {status} must not claim a captured local artifact")

    return errors

def validate_claim_source_links(claim_path: Path, source_path: Path):
    errors = []
    try:
        claims, _ = read_csv(claim_path)
        sources, _ = read_csv(source_path)
    except (OSError, UnicodeError, csv.Error) as exc:
        return [f"Unable to read linked ledgers: {exc}"]

    known = {(row.get("source_id") or "").strip() for row in sources}
    for line_no, row in enumerate(claims, start=2):
        raw = (row.get("source_ids") or "").strip()
        if not raw:
            if (row.get("status") or "").strip() != "SIMULATED":
                errors.append(f"Line {line_no}: source_ids is empty for a non-simulated claim")
            continue
        for sid in [item.strip() for item in raw.split(";") if item.strip()]:
            if sid not in known:
                errors.append(f"Line {line_no}: unknown source_id {sid}")
    return errors


def validate_artifact_source_links(artifact_path: Path, source_path: Path):
    errors = []
    try:
        artifacts, _ = read_csv(artifact_path)
        sources, _ = read_csv(source_path)
    except (OSError, UnicodeError, csv.Error) as exc:
        return [f"Unable to read linked ledgers: {exc}"]

    known = {(row.get("source_id") or "").strip() for row in sources}
    for line_no, row in enumerate(artifacts, start=2):
        raw = (row.get("source_ids") or "").strip()
        if not raw:
            errors.append(f"Line {line_no}: artifact source_ids is empty")
            continue
        for sid in [item.strip() for item in raw.split(";") if item.strip()]:
            if sid not in known:
                errors.append(f"Line {line_no}: unknown source_id {sid}")
    return errors
