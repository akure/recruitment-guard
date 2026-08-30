from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from checkpoint.v2_brief import render_v2_brief
from ops.events import make_event
from ops.review import resolve_review_item


def resolve_packet(output_root: Path, packet_id: str, actor: str, note: str) -> dict[str, Any]:
    packet_dir = output_root / f"packet_{packet_id}"
    audit_path = packet_dir / "audit.json"
    run_path = output_root / "run.json"
    if not audit_path.exists() or not run_path.exists():
        raise ValueError(f"workflow output for packet {packet_id} does not exist")
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    run = json.loads(run_path.read_text(encoding="utf-8"))
    result = next((item for item in run["packets"] if item["packet_id"] == packet_id), None)
    if result is None:
        raise ValueError(f"packet {packet_id} is not present in run.json")
    resolved = []
    for item in audit["review_items"]:
        if item["status"] != "open":
            continue
        if item["issue_type"].startswith("consent_"):
            raise ValueError("withdrawn or inactive consent cannot be resolved by reviewer override")
        updated = resolve_review_item(item, note, actor)
        resolved.append(updated)
        audit["events"].append(make_event(packet_id, "finding_resolved", actor, {"review_id": item["review_id"], "issue_type": item["issue_type"]}))
    # Replace all updated items without relying on list ordering.
    updated_by_id = {item["review_id"]: item for item in resolved}
    audit["review_items"] = [updated_by_id.get(item["review_id"], item) for item in audit["review_items"]]
    open_items = [item for item in audit["review_items"] if item["status"] == "open"]
    if not open_items and audit["consent_status"] == "granted":
        result["state"] = "finalized"
        packet_dir.joinpath("brief.md").write_text(render_v2_brief(result["bundle"], result["validation"]), encoding="utf-8")
        audit["events"].append(make_event(packet_id, "brief_exported", actor, {"evidence_only": True, "after_review": True}))
        result["events"] = audit["events"]
    audit["state"] = result["state"]
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    for item in run["packets"]:
        if item["packet_id"] == packet_id:
            item["state"] = result["state"]
            item["review_items"] = audit["review_items"]
            item["events"] = audit["events"]
    run_path.write_text(json.dumps(run, indent=2) + "\n", encoding="utf-8")
    return {"packet_id": packet_id, "state": result["state"], "resolved_count": len(resolved), "remaining_open": len(open_items)}


__all__ = ["resolve_packet"]
