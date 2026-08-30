from __future__ import annotations

from typing import Any


def _section(title: str, items: list[dict[str, Any]], evidence_by_id: dict[str, dict[str, Any]]) -> list[str]:
    lines = [f"### {title}"]
    if not items:
        lines.append("- None identified.")
        return lines
    for item in items:
        ids = item.get("evidence_ids", [])
        citations = []
        for evidence_id in ids:
            evidence = evidence_by_id.get(evidence_id)
            if evidence:
                src = evidence["source"]
                citations.append(f"{src['source_doc']}: \"{src['source_span']}\"")
        citation_text = "; ".join(citations) if citations else "No direct citation."
        lines.append(f"- **{item.get('message', item.get('claim', 'Evidence item'))}**")
        lines.append(f"  Evidence: {citation_text}")
    return lines


def render_v2_brief(bundle: dict[str, Any], validation: dict[str, Any]) -> str:
    evidence_by_id = {item["evidence_id"]: item for item in bundle["evidence"]}
    findings = validation["findings"]
    finding_by_type = {kind: [f for f in findings if f["type"] == kind] for kind in ("conflicting_evidence", "stale_evidence", "ambiguous_evidence", "uncorroborated_evidence", "missing_evidence")}
    supported = [item for item in validation["coverage"] if item["status"] == "supported"]
    unsupported = [item for item in validation["coverage"] if item["status"] != "supported"]
    lines = [
        f"## Candidate Evidence Brief — V2 Packet {bundle['packet_id']}",
        "",
        f"**Hiring profile:** {bundle['profile_id']}  ",
        f"**Role family:** {bundle['role_family']}",
        "",
        "### Supported evidence",
    ]
    if supported:
        for item in supported:
            cited = ", ".join(item["evidence_ids"]) or "no direct citation"
            lines.append(f"- **{item['text']}** — evidence IDs: {cited}")
    else:
        lines.append("- None identified.")
    lines.extend(["", "### Requirement gaps"])
    if unsupported:
        for item in unsupported:
            lines.append(f"- **{item['text']}** — no matching evidence was extracted; this is a gap for reviewer follow-up.")
    else:
        lines.append("- None identified.")
    lines.extend(["", *_section("Conflicting evidence", finding_by_type["conflicting_evidence"], evidence_by_id), "", *_section("Stale evidence", finding_by_type["stale_evidence"], evidence_by_id), "", *_section("Ambiguous evidence", finding_by_type["ambiguous_evidence"], evidence_by_id), "", *_section("Uncorroborated evidence", finding_by_type["uncorroborated_evidence"], evidence_by_id), "", "### Questions for reviewer"])
    for question in bundle["review_questions"]:
        lines.append(f"- {question}")
    if not bundle["review_questions"]:
        lines.append("- None identified.")
    lines.extend(["", "---", "This brief presents evidence only. It contains no hire/no-hire recommendation or score."])
    if any(f["severity"] == "block" for f in findings):
        lines.append("All blocking items above require human review before this brief is treated as complete.")
    return "\n".join(lines) + "\n"
