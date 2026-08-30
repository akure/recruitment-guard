from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from checkpoint.v2_brief import render_v2_brief
from extraction.v2_extract import extract_packet
from ops.review import create_review_item
from validator.v2_validate import validate_v2
from workflow.importer import import_source
from workflow.review import resolve_packet


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def process_packet(record: dict[str, Any], as_of: date, owner: str, due_at: str | None = None) -> dict[str, Any]:
    packet = Path(record["packet_path"]).resolve() if record.get("packet_path") else None
    if packet is None or not packet.is_dir():
        raise ValueError("workflow records require an internal packet_path")
    bundle = extract_packet(packet, mock=True)
    assessment_path = packet / "assessment.json"
    assessment = json.loads(assessment_path.read_text(encoding="utf-8")) if assessment_path.exists() else None
    validation = validate_v2(bundle, assessment=assessment, as_of=as_of)
    if record["consent_status"] != "granted":
        validation["findings"].insert(0, {
            "finding_id": f"consent-{bundle['packet_id']}",
            "type": "consent_withdrawn" if record["consent_status"] == "withdrawn" else "consent_inactive",
            "severity": "block",
            "message": "Consent is not active; do not finalize or export a candidate evidence brief.",
            "evidence_ids": [],
        })
        validation["blocking"] = True
    review_items = [
        create_review_item(bundle["packet_id"], finding["type"], finding.get("evidence_ids", []), owner, due_at=due_at)
        for finding in validation["findings"]
        if finding["severity"] == "block"
    ]
    events = list(record.get("events", []))
    if validation["blocking"]:
        events.append({
            "event_id": f"review-requested-{bundle['packet_id']}",
            "packet_id": bundle["packet_id"],
            "event_type": "review_requested",
            "actor_type": "system",
            "occurred_at": _now(),
            "payload": {"finding_count": len(review_items)},
        })
    else:
        events.append({
            "event_id": f"brief-exported-{bundle['packet_id']}",
            "packet_id": bundle["packet_id"],
            "event_type": "brief_exported",
            "actor_type": "system",
            "occurred_at": _now(),
            "payload": {"evidence_only": True},
        })
    return {
        "packet_id": bundle["packet_id"],
        "profile_id": bundle["profile_id"],
        "role_family": bundle["role_family"],
        "consent_id": record["consent_id"],
        "consent_status": record["consent_status"],
        "state": "pending_review" if validation["blocking"] else "finalized",
        "bundle": bundle,
        "validation": validation,
        "review_items": review_items,
        "events": events,
        "source_files": record["source_files"],
        "ingestion_source": record["ingestion_source"],
    }


def run(source: Path, output_root: Path, as_of: date, owner: str, due_at: str | None = None) -> dict[str, Any]:
    records = import_source(source)
    results = [process_packet(record, as_of, owner, due_at) for record in records]
    output_root.mkdir(parents=True, exist_ok=True)
    for result in results:
        packet_dir = output_root / f"packet_{result['packet_id']}"
        packet_dir.mkdir(parents=True, exist_ok=True)
        audit = dict(result)
        audit.pop("bundle", None)
        (packet_dir / "audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
        if result["state"] == "finalized":
            (packet_dir / "brief.md").write_text(render_v2_brief(result["bundle"], result["validation"]), encoding="utf-8")
    summary = {
        "packet_count": len(results),
        "states": {state: sum(item["state"] == state for item in results) for state in ("finalized", "pending_review")},
        "output_root": str(output_root.resolve()),
    }
    (output_root / "run.json").write_text(json.dumps({"summary": summary, "packets": results}, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Import, validate, review, and export RecruitmentGuard evidence packets.")
    parser.add_argument("source", type=Path, nargs="?", help="packet folder, folder of packet_* directories, CSV, or JSON manifest")
    parser.add_argument("--output-root", type=Path, default=Path("workflow_output"))
    parser.add_argument("--as-of", default=date.today().isoformat())
    parser.add_argument("--owner", default="recruiter", help="owner assigned to blocking review items")
    parser.add_argument("--due-at", help="ISO-8601 due date/time for blocking review items")
    parser.add_argument("--resolve-packet", help="resolve all open non-consent findings for a prior packet run")
    parser.add_argument("--actor", default="recruiter", help="reviewer actor for resolution")
    parser.add_argument("--resolution-note", help="resolution note for the reviewer action")
    args = parser.parse_args()
    if args.resolve_packet:
        if not args.resolution_note:
            parser.error("--resolution-note is required with --resolve-packet")
        print(json.dumps(resolve_packet(args.output_root, args.resolve_packet, args.actor, args.resolution_note), indent=2))
    else:
        if not args.source:
            parser.error("source is required unless --resolve-packet is used")
        print(json.dumps(run(args.source, args.output_root, date.fromisoformat(args.as_of), args.owner, args.due_at), indent=2))


if __name__ == "__main__":
    main()
