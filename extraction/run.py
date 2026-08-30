from __future__ import annotations

import argparse
import json
from pathlib import Path

from extract import extract_document


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract structured CV/transcript facts for all candidate packets.")
    parser.add_argument("--data", default="data", help="dataset root")
    parser.add_argument("--output", default="extraction/output", help="artifact output root")
    parser.add_argument("--mock", action="store_true", help="use local deterministic extraction")
    args = parser.parse_args()

    data_root = Path(args.data)
    output_root = Path(args.output)
    packets = sorted(data_root.glob("packet_*"))
    if len(packets) != 12:
        raise SystemExit(f"expected 12 packets, found {len(packets)}")

    for packet in packets:
        packet_id = packet.name.rsplit("_", 1)[-1]
        artifact = {"packet_id": packet_id, "cv": None, "transcript": None, "model_calls": []}
        for doc in ("cv", "transcript"):
            result, usage = extract_document(packet / f"{doc}.md", doc, packet_id, mock=args.mock)
            artifact[doc] = result
            artifact["model_calls"].append({"stage": "extraction", "doc": doc, **usage})
        destination = output_root / f"packet_{packet_id}.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
        print(destination)


if __name__ == "__main__":
    main()
