from __future__ import annotations

import argparse
import os
from pathlib import Path

PROMPT = """Summarize this synthetic Backend Engineer candidate packet for a hiring manager.
Describe relevant experience and evidence from the CV and interview transcript.
Do not make a hire/no-hire recommendation, score, or ranking. If sources disagree,
write a coherent summary without adding facts not present in the packet."""


def mock_brief(packet_id: str, cv: str, transcript: str) -> str:
    return f"""## Candidate Evidence Brief — Packet {packet_id} — Backend Engineer

### Summary

The candidate's CV describes the following experience:

> {cv.strip()}

The interview transcript provides the following context:

> {transcript.strip()}

### Note

This baseline is a plain summarization comparison path. It does not perform structured extraction, contradiction validation, or human checkpointing. This brief presents evidence only and contains no hire/no-hire recommendation, score, or ranking.
"""


def llm_brief(packet_id: str, cv: str, transcript: str) -> str:
    from openai import OpenAI

    client = OpenAI()
    response = client.chat.completions.create(
        model=os.getenv("RECRUITMENT_GUARD_MODEL", "gpt-5-mini"),
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": f"Packet {packet_id}\n\nCV:\n{cv}\n\nTranscript:\n{transcript}"},
        ],
        max_completion_tokens=1800,
    )
    return response.choices[0].message.content


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", help="path to data/packet_NN")
    parser.add_argument("--output", help="output markdown path")
    parser.add_argument("--mock", action="store_true", help="use local deterministic output")
    args = parser.parse_args()
    packet = Path(args.packet)
    packet_id = packet.name.rsplit("_", 1)[-1]
    cv = (packet / "cv.md").read_text(encoding="utf-8")
    transcript = (packet / "transcript.md").read_text(encoding="utf-8")
    brief = mock_brief(packet_id, cv, transcript) if args.mock else llm_brief(packet_id, cv, transcript)
    output = Path(args.output) if args.output else Path("briefs") / f"brief_baseline_{packet_id}.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(brief.rstrip() + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
