from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

ALLOWED_PURPOSES = {"recruiting_review", "assessment_review", "workflow_analytics"}
ALLOWED_SCOPE = {"resume", "transcript", "assessment", "work_preferences", "authorization_workflow"}


def validate_consent(record: dict[str, Any], require_active: bool = False) -> bool:
    required = {"consent_id", "packet_id", "subject_type", "purpose", "scope", "status", "recorded_at", "retention_days", "source"}
    missing = required - set(record)
    if missing:
        raise ValueError(f"consent record missing fields: {sorted(missing)}")
    if record["subject_type"] != "candidate":
        raise ValueError("consent subject_type must be candidate")
    if record["purpose"] not in ALLOWED_PURPOSES:
        raise ValueError("unsupported consent purpose")
    if not record["scope"] or not set(record["scope"]).issubset(ALLOWED_SCOPE):
        raise ValueError("consent scope must contain approved values")
    if record["status"] not in {"granted", "withdrawn", "expired"}:
        raise ValueError("unsupported consent status")
    if not isinstance(record["retention_days"], int) or not 1 <= record["retention_days"] <= 3650:
        raise ValueError("retention_days must be between 1 and 3650")
    datetime.fromisoformat(record["recorded_at"].replace("Z", "+00:00"))
    if record.get("withdrawn_at"):
        datetime.fromisoformat(record["withdrawn_at"].replace("Z", "+00:00"))
    if require_active and record["status"] != "granted":
        return False
    return True
