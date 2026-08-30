from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from extraction.v2_extract import extract_packet
from validator.v2_validate import validate_v2
from eval.v2_harness import evaluate_v2_records, render_v2_metrics


def _citation_fidelity(bundle: dict, packet: Path) -> float:
    checks = []
    for item in bundle["evidence"]:
        source = (packet / f"{item['source']['source_doc']}.md").read_text(encoding="utf-8")
        start, end = item["source"]["span_offset"]
        checks.append(source[start:end] == item["source"]["source_span"])
    for item in bundle["requirements"]:
        source = (packet / "jd.md").read_text(encoding="utf-8")
        start, end = item["source"]["span_offset"]
        checks.append(source[start:end] == item["source"]["source_span"])
    return sum(checks) / len(checks) if checks else 1.0


def run(data_root: Path, as_of: date) -> tuple[list[dict], dict]:
    records = []
    for packet in sorted(data_root.glob("packet_*")):
        bundle = extract_packet(packet, mock=True)
        truth = json.loads((packet / "ground_truth.json").read_text(encoding="utf-8"))
        assessment_path = packet / "assessment.json"
        assessment = json.loads(assessment_path.read_text(encoding="utf-8")) if assessment_path.exists() else None
        validation = validate_v2(bundle, assessment=assessment, as_of=as_of)
        records.append({
            "packet_id": bundle["packet_id"],
            "profile_id": bundle["profile_id"],
            "role_family": bundle["role_family"],
            "condition": truth["evidence_condition"],
            "findings": validation["findings"],
            "state": "pending_review" if validation["blocking"] else "finalized",
            "citation_fidelity": _citation_fidelity(bundle, packet),
            "review_questions": len(bundle["review_questions"]),
        })
    return records, evaluate_v2_records(records)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=Path("data_v2"))
    parser.add_argument("--output-root", type=Path, default=Path("eval"))
    parser.add_argument("--as-of", default="2026-08-30")
    args = parser.parse_args()
    records, summary = run(args.data_root, date.fromisoformat(args.as_of))
    args.output_root.mkdir(parents=True, exist_ok=True)
    (args.output_root / "v2_results.json").write_text(json.dumps({"records": records, "summary": summary}, indent=2) + "\n", encoding="utf-8")
    (args.output_root / "v2_metrics.md").write_text(render_v2_metrics(summary), encoding="utf-8")
    print(json.dumps({"packet_count": len(records), "output": str(args.output_root)}, indent=2))


if __name__ == "__main__":
    main()
