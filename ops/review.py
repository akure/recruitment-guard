from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def create_review_item(packet_id: str, issue_type: str, evidence_ids: list[str], owner: str, due_at: str | None = None) -> dict[str, Any]:
    if not owner.strip():
        raise ValueError("review item requires an owner")
    if not issue_type.strip():
        raise ValueError("review item requires an issue type")
    return {
        "review_id": f"review-{uuid4().hex[:12]}",
        "packet_id": packet_id,
        "issue_type": issue_type,
        "evidence_ids": list(evidence_ids),
        "owner": owner,
        "status": "open",
        "due_at": due_at,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "resolution": None,
    }


def resolve_review_item(item: dict[str, Any], note: str, actor: str) -> dict[str, Any]:
    if item.get("status") != "open":
        raise ValueError("only open review items can be resolved")
    if not note.strip():
        raise ValueError("resolution requires a note")
    if not actor.strip():
        raise ValueError("resolution requires an actor")
    resolved = dict(item)
    resolved["status"] = "resolved"
    resolved["resolution"] = {
        "note": note,
        "actor": actor,
        "resolved_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    return resolved
