from __future__ import annotations

import argparse
import json
from pathlib import Path

from validator.validate import ValidatorFinding
from .workflow import create_pending_review


def main() -> None:
    parser = argparse.ArgumentParser(description="Pause a packet for recruiter review.")
    parser.add_argument("packet_id")
    parser.add_argument("findings_json", help="JSON file containing a ValidatorFinding[]")
    parser.add_argument("--pending-dir", default="pending_review")
    args = parser.parse_args()
    raw_findings = json.loads(Path(args.findings_json).read_text(encoding="utf-8"))
    findings = [ValidatorFinding(**item) for item in raw_findings]
    path = Path(args.pending_dir) / f"packet_{args.packet_id.zfill(2)}.json"
    create_pending_review(args.packet_id.zfill(2), findings, path)
    print(path)


if __name__ == "__main__":
    main()
