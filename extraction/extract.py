from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

TAXONOMY = (
    "team_size_",
    "ownership_",
    "skill_claim_",
    "skill_demonstrated_",
    "tenure_",
)

PROMPT = """Extract only material facts matching one of these subject prefixes:
team_size_<project_slug>, ownership_<project_slug>, skill_claim_<skill_slug>,
skill_demonstrated_<skill_slug>, tenure_<company_slug>.
Quote source_span verbatim from the document. Do not infer, paraphrase, or force-fit.
Return JSON with source_doc, packet_id, and facts[]."""


def _validate(data: dict[str, Any], source: str, source_doc: str, packet_id: str) -> dict[str, Any]:
    if data.get("source_doc") != source_doc or data.get("packet_id") != packet_id:
        raise ValueError("extraction metadata does not match the requested document")
    facts = data.get("facts")
    if not isinstance(facts, list):
        raise ValueError("facts must be a list")
    for index, fact in enumerate(facts, start=1):
        if not all(key in fact for key in ("fact_id", "subject", "claim", "source_span", "span_offset")):
            raise ValueError(f"fact {index} is missing a required field")
        if not fact["subject"].startswith(TAXONOMY):
            raise ValueError(f"fact {index} uses an unsupported subject: {fact['subject']}")
        span = fact["source_span"]
        if span not in source:
            raise ValueError(f"fact {index} source_span is not a verbatim substring")
        starts = [match.start() for match in re.finditer(re.escape(span), source)]
        if not starts:
            raise ValueError(f"fact {index} source_span is not a verbatim substring")
        if len(starts) > 1:
            raise ValueError(f"fact {index} source_span is ambiguous ({len(starts)} matches)")
        expected = [starts[0], starts[0] + len(span)]
        if fact["span_offset"] != expected:
            # Models occasionally quote the right text but count offsets poorly.
            # Repair is safe only for one exact, unique substring; ambiguity fails closed.
            fact["span_offset"] = expected
    return data


def _mock_extract(source: str, source_doc: str, packet_id: str) -> dict[str, Any]:
    facts: list[dict[str, Any]] = []

    def add(subject: str, phrase: str, claim: str | None = None) -> None:
        start = source.find(phrase)
        if start >= 0:
            facts.append({
                "fact_id": f"{source_doc[:1]}{len(facts) + 1}",
                "subject": subject,
                "claim": claim or phrase,
                "source_span": phrase,
                "span_offset": [start, start + len(phrase)],
            })

    team = re.search(r"team of (\d+ engineers?)", source, re.I)
    if team:
        project = "payments_migration" if "payments migration" in source.lower() else "service"
        add(f"team_size_{project}", team.group(0))
    if "payments migration" in source.lower():
        add("ownership_payments_migration", "owning architecture and delivery")
        add("ownership_payments_migration", "drove the whole thing solo")
        if source_doc == "transcript":
            add("team_size_payments_migration", "mostly me. I had code review from one senior engineer but I drove the whole thing solo.")
    if "distributed systems" in source.lower() or "consistency guarantees" in source.lower():
        if source_doc == "cv":
            add("skill_claim_distributed_systems", "Expert in distributed systems")
        else:
            add("skill_demonstrated_distributed_systems", "we just made sure the database was replicated")
            add("skill_claim_distributed_systems", "I didn't really need to think about it much beyond that.")
    if "backend experience" in source.lower():
        match = re.search(r"(\d+ years of backend experience)", source, re.I)
        if match:
            add("tenure_backend_engineering", match.group(1))
    return _validate({"source_doc": source_doc, "packet_id": packet_id, "facts": facts}, source, source_doc, packet_id)


def _llm_extract(source: str, source_doc: str, packet_id: str) -> tuple[dict[str, Any], dict[str, int]]:
    from openai import OpenAI

    schema = {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "source_doc": {"type": "string", "enum": ["cv", "transcript"]},
            "packet_id": {"type": "string"},
            "facts": {"type": "array", "items": {
                "type": "object", "additionalProperties": False,
                "required": ["fact_id", "subject", "claim", "source_span", "span_offset"],
                "properties": {
                    "fact_id": {"type": "string"},
                    "subject": {"type": "string"},
                    "claim": {"type": "string"},
                    "source_span": {"type": "string"},
                    "span_offset": {"type": "array", "items": {"type": "integer"}, "minItems": 2, "maxItems": 2},
                },
            }},
        },
        "required": ["source_doc", "packet_id", "facts"],
    }
    client = OpenAI(timeout=float(os.getenv("RECRUITMENT_GUARD_TIMEOUT", "45")), max_retries=1)
    response = client.chat.completions.create(
        model=os.getenv("RECRUITMENT_GUARD_MODEL", "gpt-5-mini"),
        messages=[
            {"role": "system", "content": PROMPT},
            {"role": "user", "content": f"source_doc={source_doc}; packet_id={packet_id}\n\n{source}"},
        ],
        response_format={"type": "json_schema", "json_schema": {"name": "extracted_fact_set", "strict": True, "schema": schema}},
        max_completion_tokens=1600,
    )
    data = json.loads(response.choices[0].message.content)
    usage = {"tokens_in": response.usage.prompt_tokens, "tokens_out": response.usage.completion_tokens}
    return _validate(data, source, source_doc, packet_id), usage


def extract_document(path: Path, source_doc: str, packet_id: str, mock: bool = False) -> tuple[dict[str, Any], dict[str, int]]:
    source = path.read_text(encoding="utf-8")
    if mock:
        return _mock_extract(source, source_doc, packet_id), {"tokens_in": 0, "tokens_out": 0}
    return _llm_extract(source, source_doc, packet_id)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", help="path to data/packet_NN")
    parser.add_argument("--mock", action="store_true", help="use local deterministic extraction for smoke tests")
    args = parser.parse_args()
    packet = Path(args.packet)
    packet_id = packet.name.rsplit("_", 1)[-1]
    output = {"cv": None, "transcript": None, "model_calls": []}
    for doc in ("cv", "transcript"):
        result, usage = extract_document(packet / f"{doc}.md", doc, packet_id, mock=args.mock)
        output[doc] = result
        output["model_calls"].append({"stage": "extraction", "doc": doc, **usage})
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
