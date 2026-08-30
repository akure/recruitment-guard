from __future__ import annotations

import argparse
import json
from pathlib import Path

from extraction.v2_extract import extract_packet


def run(data_root: Path, output_root: Path) -> list[dict]:
    output_root.mkdir(parents=True, exist_ok=True)
    records = []
    for packet in sorted(data_root.glob("packet_*")):
        bundle = extract_packet(packet, mock=True)
        out = output_root / f"packet_{bundle['packet_id']}.json"
        out.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
        records.append({
            "packet_id": bundle["packet_id"],
            "profile_id": bundle["profile_id"],
            "role_family": bundle["role_family"],
            "requirements": len(bundle["requirements"]),
            "evidence": len(bundle["evidence"]),
            "review_questions": len(bundle["review_questions"]),
            "mode": "mock",
            "output": str(out),
        })
    manifest = {"schema_version": "v2.1", "packet_count": len(records), "records": records}
    (output_root / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=Path("data_v2"))
    parser.add_argument("--output-root", type=Path, default=Path("extraction/v2_output"))
    args = parser.parse_args()
    records = run(args.data_root, args.output_root)
    print(json.dumps({"packet_count": len(records), "output": str(args.output_root)}, indent=2))


if __name__ == "__main__":
    main()
