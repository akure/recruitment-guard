from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from .workflow import Assessment, ExtractedFact, finalize_packet


def _facts(artifact: dict, doc: str) -> list[ExtractedFact]:
    return [
        ExtractedFact(
            fact_id=fact["fact_id"],
            subject=fact["subject"],
            claim=fact["claim"],
            source_doc=doc,
            source_span=fact["source_span"],
        )
        for fact in artifact[doc]["facts"]
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Finalize a reviewed candidate evidence brief.")
    parser.add_argument("packet_id")
    parser.add_argument("--extraction-dir", default="extraction/output")
    parser.add_argument("--data-dir", default="data")
    parser.add_argument("--pending-dir", default="pending_review")
    parser.add_argument("--brief-dir", default="briefs")
    args = parser.parse_args()

    packet_id = args.packet_id.zfill(2)
    artifact = json.loads((Path(args.extraction_dir) / f"packet_{packet_id}.json").read_text(encoding="utf-8"))
    assessment_path = Path(args.data_dir) / f"packet_{packet_id}" / "assessment.json"
    assessment = None
    if assessment_path.exists():
        raw = json.loads(assessment_path.read_text(encoding="utf-8"))
        assessment = Assessment(raw["score"], date.fromisoformat(raw["date"]))
    pending = Path(args.pending_dir) / f"packet_{packet_id}.json"
    brief = Path(args.brief_dir) / f"brief_guarded_{packet_id}.md"
    output = finalize_packet(packet_id, pending, brief, _facts(artifact, "cv"), _facts(artifact, "transcript"), assessment)
    print(output)


if __name__ == "__main__":
    main()
