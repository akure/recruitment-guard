from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Iterable

from validator.validate import Assessment, ExtractedFact, ValidatorFinding


def _finding_dict(finding: ValidatorFinding | dict) -> dict:
    return finding.as_dict() if isinstance(finding, ValidatorFinding) else dict(finding)


def create_pending_review(packet_id: str, findings: Iterable[ValidatorFinding], path: Path) -> Path:
    payload = {
        "packet_id": packet_id,
        "state": "pending_review",
        "findings": [_finding_dict(finding) for finding in findings],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def resolve_finding(path: Path, finding_id: str, note: str) -> Path:
    payload = json.loads(path.read_text(encoding="utf-8"))
    for finding in payload.get("findings", []):
        if finding.get("finding_id") == finding_id:
            finding["resolution"] = note
            path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            return path
    raise KeyError(f"finding not found: {finding_id}")


def _open_blocking_findings(payload: dict) -> list[dict]:
    return [
        finding for finding in payload.get("findings", [])
        if finding.get("severity") == "block" and not finding.get("resolution")
    ]


def _load_findings(pending_path: Path | None) -> tuple[list[dict], dict | None]:
    if pending_path is None or not pending_path.exists():
        return [], None
    payload = json.loads(pending_path.read_text(encoding="utf-8"))
    return payload.get("findings", []), payload


def _source_label(doc: str) -> str:
    return {"cv": "CV", "transcript": "Transcript", "assessment": "Assessment"}.get(doc, doc.title())


def _render_finding(finding: dict) -> str:
    subject = finding.get("subject", "unknown")
    sources = finding.get("sources", [])
    if finding.get("type") == "contradiction" and len(sources) >= 2:
        description = f"{_source_label(sources[0]['doc'])} states \"{sources[0]['span']}\" while { _source_label(sources[1]['doc']) } states \"{sources[1]['span']}\"."
    elif finding.get("type") == "missing_evidence":
        description = "No assessment score is present in the packet."
    elif finding.get("type") == "stale_evidence":
        description = f"The assessment evidence is older than the configured freshness threshold ({sources[0]['span'] if sources else 'date unavailable'})."
    else:
        description = "A material evidence issue was flagged."
    return f"- **{finding.get('type')} ({subject}):** {description}\n  Resolution: {finding.get('resolution')}"


def render_brief(
    packet_id: str,
    cv_facts: Iterable[ExtractedFact],
    transcript_facts: Iterable[ExtractedFact],
    assessment: Assessment | None,
    findings: Iterable[ValidatorFinding | dict],
) -> str:
    all_facts = list(cv_facts) + list(transcript_facts)
    finding_dicts = [_finding_dict(finding) for finding in findings]
    lines = [
        f"## Candidate Evidence Brief — Packet {packet_id} — Backend Engineer (Series B fintech)",
        "",
        "### Evidence summary",
    ]
    if all_facts:
        for fact in all_facts:
            lines.append(f'- Claim: "{fact.claim}" — Source: {_source_label(fact.source_doc)}, "{fact.source_span}"')
    else:
        lines.append("- No structured claims were extracted for this brief.")

    contradictions = [f for f in finding_dicts if f.get("type") == "contradiction"]
    gaps = [f for f in finding_dicts if f.get("type") in {"missing_evidence", "stale_evidence"}]
    if finding_dicts:
        lines.extend(["", "### ⚠ Flagged for review"])
        lines.extend(_render_finding(finding) for finding in finding_dicts if finding not in gaps)
    if gaps:
        lines.extend(["", "### Gaps"])
        for finding in gaps:
            lines.append(_render_finding(finding))
    elif assessment is not None:
        lines.extend(["", "### Gaps", "- No assessment freshness or completeness gap was identified."])

    lines.extend(["", "---", "This brief presents evidence only. It contains no hire/no-hire recommendation or score."])
    if finding_dicts:
        lines.append("All flagged items above were reviewed and resolved by a human before this brief was finalized.")
    return "\n".join(lines) + "\n"


def finalize_packet(
    packet_id: str,
    pending_path: Path | None,
    brief_path: Path,
    cv_facts: Iterable[ExtractedFact],
    transcript_facts: Iterable[ExtractedFact],
    assessment: Assessment | None,
) -> Path:
    findings, payload = _load_findings(pending_path)
    open_findings = _open_blocking_findings(payload or {"findings": findings})
    if open_findings:
        ids = ", ".join(finding["finding_id"] for finding in open_findings)
        raise PermissionError(f"cannot finalize packet {packet_id}; unresolved findings: {ids}")
    brief_path.parent.mkdir(parents=True, exist_ok=True)
    brief_path.write_text(render_brief(packet_id, cv_facts, transcript_facts, assessment, findings), encoding="utf-8")
    if payload is not None:
        payload["state"] = "finalized"
        pending_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return brief_path
