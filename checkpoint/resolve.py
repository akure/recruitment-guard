from __future__ import annotations

import argparse
from pathlib import Path

from .workflow import resolve_finding


def main() -> None:
    parser = argparse.ArgumentParser(description="Record a recruiter resolution for one pending finding.")
    parser.add_argument("packet_id")
    parser.add_argument("--finding", required=True)
    parser.add_argument("--note", required=True)
    parser.add_argument("--pending-dir", default="pending_review")
    args = parser.parse_args()
    path = Path(args.pending_dir) / f"packet_{args.packet_id}.json"
    resolve_finding(path, args.finding, args.note)
    print(f"resolved {args.finding} for packet {args.packet_id}")


if __name__ == "__main__":
    main()
