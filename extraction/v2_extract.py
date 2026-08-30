from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "v2.1"
QUALITY_VALUES = {"direct", "specific", "ambiguous", "uncorroborated", "uncertain"}


def _span(source_doc: str, source: str, text: str) -> dict[str, Any]:
    start = source.find(text)
    if start < 0:
        raise ValueError(f"source span not found in {source_doc}: {text!r}")
    return {"source_doc": source_doc, "source_span": text, "span_offset": [start, start + len(text)]}


def _slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:60]


def _quality(text: str, source_doc: str) -> tuple[str, float]:
    lower = text.lower()
    if any(word in lower for word in ("ambiguous", "parts of", "shared the final", "outcomes")):
        return "ambiguous", 0.62
    if any(word in lower for word in ("confirm", "would want to", "varied by", "exact percentage")):
        return "uncertain", 0.58
    if source_doc == "transcript" and any(word in lower for word in ("helped", "worked on", "contributed")):
        return "uncorroborated", 0.64
    if re.search(r"\b\d+%\b|\b20\d\d\b|\bowned\b|\bimplemented\b|\bbuilt\b|\boperated\b", lower):
        return "specific", 0.86
    return "direct", 0.76


def _evidence_kind(text: str) -> str:
    lower = text.lower()
    if any(word in lower for word in ("2021", "2022", "present", "years")):
        return "timeline"
    if any(word in lower for word in ("python", "go", "java", "typescript", "scala", "terraform")):
        return "technology"
    if any(word in lower for word in ("owned", "led", "implemented", "built", "delivered", "reduced")):
        return "accomplishment"
    if any(word in lower for word in ("partnered", "communicat", "ambiguous", "trade-off")):
        return "working_style"
    if text.startswith("**"):
        return "interview_answer"
    return "scope"


def _load_context(packet: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    profile = json.loads((packet / "profile.json").read_text(encoding="utf-8"))
    role_file = packet / "role_family.json"
    if role_file.exists():
        role = json.loads(role_file.read_text(encoding="utf-8"))
    else:
        role_id = json.loads((packet / "ground_truth.json").read_text(encoding="utf-8"))["role_family"]
        role = json.loads((packet.parent / "role_families" / f"{role_id}.json").read_text(encoding="utf-8"))
    truth = json.loads((packet / "ground_truth.json").read_text(encoding="utf-8"))
    return profile, role, truth


def _requirements(packet: Path, profile: dict[str, Any], role: dict[str, Any]) -> list[dict[str, Any]]:
    source = (packet / "jd.md").read_text(encoding="utf-8")
    requirements: list[dict[str, Any]] = []
    current_priority = "must_have"
    counter = 1
    for line in source.splitlines(keepends=False):
        stripped = line.strip()
        if stripped.lower().startswith("## preferred"):
            current_priority = "preferred"
        if not stripped.startswith("- "):
            continue
        text = stripped[2:].strip()
        requirements.append({
            "requirement_id": f"r{counter}",
            "text": text,
            "priority": current_priority,
            "source": _span("jd", source, line),
        })
        counter += 1
    if not requirements:
        raise ValueError("V2 JD contains no bullet requirements")
    return requirements


def _candidate_evidence(packet: Path, role_family: str) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = []
    counter = 1
    for source_doc in ("cv", "transcript"):
        source = (packet / f"{source_doc}.md").read_text(encoding="utf-8")
        lines = [line for line in source.splitlines() if line.strip().startswith("- ") or line.strip().startswith("**") or (source_doc == "cv" and re.search(r"20\d\d[–-]", line))]
        for line in lines:
            text = line.strip()
            if text.startswith("**") and ":**" in text:
                text = text.split(":**", 1)[1].strip()
            if not text:
                continue
            quality, confidence = _quality(text, source_doc)
            keyword = next((word for word in re.findall(r"[A-Za-z][A-Za-z-]+", text.lower()) if len(word) > 5), role_family)
            corroboration = []
            other_doc = "transcript" if source_doc == "cv" else "cv"
            other_source = (packet / f"{other_doc}.md").read_text(encoding="utf-8")
            if keyword in other_source.lower():
                corroboration.append(other_doc)
            evidence.append({
                "evidence_id": f"e{counter}",
                "subject": f"{role_family}:{_slug(keyword)}",
                "claim": text,
                "evidence_kind": _evidence_kind(text),
                "evidence_quality": quality,
                "confidence": confidence,
                "source": _span(source_doc, source, line),
                "corroboration": corroboration,
            })
            counter += 1
    if not evidence:
        raise ValueError(f"no candidate evidence found for {packet}")
    return evidence


def validate_bundle(bundle: dict[str, Any], packet: Path) -> dict[str, Any]:
    required = {"schema_version", "packet_id", "profile_id", "role_family", "requirements", "evidence", "review_questions"}
    missing = required - set(bundle)
    if missing:
        raise ValueError(f"bundle missing fields: {sorted(missing)}")
    if bundle["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unsupported V2 evidence schema version")
    for requirement in bundle["requirements"]:
        source = (packet / "jd.md").read_text(encoding="utf-8")
        span = requirement["source"]
        start, end = span["span_offset"]
        if source[start:end] != span["source_span"]:
            raise ValueError(f"invalid JD span for {requirement['requirement_id']}")
    for item in bundle["evidence"]:
        source = (packet / f"{item['source']['source_doc']}.md").read_text(encoding="utf-8")
        span = item["source"]
        start, end = span["span_offset"]
        if source[start:end] != span["source_span"]:
            raise ValueError(f"invalid evidence span for {item['evidence_id']}")
        if item["evidence_quality"] not in QUALITY_VALUES:
            raise ValueError(f"invalid evidence quality for {item['evidence_id']}")
        if not 0 <= item["confidence"] <= 1:
            raise ValueError(f"invalid confidence for {item['evidence_id']}")
    return bundle


def extract_packet(packet: Path, mock: bool = False) -> dict[str, Any]:
    profile, role, truth = _load_context(packet)
    bundle = {
        "schema_version": SCHEMA_VERSION,
        "packet_id": truth["packet_id"],
        "profile_id": profile["profile_id"],
        "role_family": truth["role_family"],
        "requirements": _requirements(packet, profile, role),
        "evidence": _candidate_evidence(packet, truth["role_family"]),
        "review_questions": profile["evidence_policies"]["review_questions"],
    }
    return validate_bundle(bundle, packet)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("packet", type=Path)
    parser.add_argument("--mock", action="store_true", help="use deterministic extraction")
    args = parser.parse_args()
    print(json.dumps(extract_packet(args.packet, mock=args.mock), indent=2))


if __name__ == "__main__":
    main()
