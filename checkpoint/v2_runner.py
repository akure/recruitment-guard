from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from checkpoint.v2_brief import render_v2_brief
from extraction.v2_extract import extract_packet
from validator.v2_validate import validate_v2


def run_packet(packet: Path, brief_root: Path, pending_root: Path, as_of: date) -> dict:
    bundle = extract_packet(packet, mock=True)
    assessment_path = packet / "assessment.json"
    assessment = json.loads(assessment_path.read_text(encoding="utf-8")) if assessment_path.exists() else None
    validation = validate_v2(bundle, assessment=assessment, as_of=as_of)
    result = {"packet_id": bundle["packet_id"], "profile_id": bundle["profile_id"], "role_family": bundle["role_family"], "state": "pending_review" if validation["blocking"] else "finalized", "findings": validation["findings"]}
    if validation["blocking"]:
        pending_root.mkdir(parents=True, exist_ok=True)
        (pending_root / f"packet_{bundle['packet_id']}.json").write_text(json.dumps({"bundle": bundle, "validation": validation, "resolution": None}, indent=2) + "\n", encoding="utf-8")
    else:
        brief_root.mkdir(parents=True, exist_ok=True)
        brief_path = brief_root / f"brief_v2_{bundle['packet_id']}.md"
        brief_path.write_text(render_v2_brief(bundle, validation), encoding="utf-8")
        result["brief"] = str(brief_path)
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=Path("data_v2"))
    parser.add_argument("--brief-root", type=Path, default=Path("briefs/v2"))
    parser.add_argument("--pending-root", type=Path, default=Path("pending_review/v2"))
    parser.add_argument("--as-of", default="2026-08-30")
    args = parser.parse_args()
    results = [run_packet(packet, args.brief_root, args.pending_root, date.fromisoformat(args.as_of)) for packet in sorted(args.data_root.glob("packet_*"))]
    print(json.dumps({"packet_count": len(results), "states": {state: sum(item["state"] == state for item in results) for state in ("finalized", "pending_review")}}, indent=2))


if __name__ == "__main__":
    main()
