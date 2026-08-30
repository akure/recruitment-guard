from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

EVENT_TYPES = {"packet_ingested", "extraction_completed", "validation_completed", "review_requested", "finding_resolved", "brief_exported", "consent_recorded", "consent_withdrawn"}
ACTOR_TYPES = {"system", "recruiter", "hiring_manager", "candidate"}


def make_event(packet_id: str, event_type: str, actor_type: str, payload: dict[str, Any], occurred_at: str | None = None) -> dict[str, Any]:
    if event_type not in EVENT_TYPES:
        raise ValueError(f"unsupported event_type: {event_type}")
    if actor_type not in ACTOR_TYPES:
        raise ValueError(f"unsupported actor_type: {actor_type}")
    return {
        "event_id": f"evt-{uuid4().hex[:12]}",
        "packet_id": packet_id,
        "event_type": event_type,
        "actor_type": actor_type,
        "occurred_at": occurred_at or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "payload": payload,
    }
