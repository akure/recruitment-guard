from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Any

BLOCKING = {"conflicting_evidence", "missing_evidence", "stale_evidence"}


def _words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 3}


def _finding(kind: str, severity: str, message: str, evidence_ids: list[str] | None = None) -> dict[str, Any]:
    return {"finding_id": f"v2-{kind}-{len(message)}", "type": kind, "severity": severity, "message": message, "evidence_ids": evidence_ids or []}


def _coverage(requirements: list[dict[str, Any]], evidence: list[dict[str, Any]]) -> list[dict[str, Any]]:
    corpus = [(item, _words(item["claim"])) for item in evidence]
    results = []
    for requirement in requirements:
        req_words = _words(requirement["text"])
        matches = [item["evidence_id"] for item, words in corpus if req_words & words]
        results.append({
            "requirement_id": requirement["requirement_id"],
            "text": requirement["text"],
            "priority": requirement["priority"],
            "status": "supported" if matches else "not_evidenced",
            "evidence_ids": matches,
        })
    return results


def _conflict(bundle: dict[str, Any]) -> dict[str, Any] | None:
    cv = [item for item in bundle["evidence"] if item["source"]["source_doc"] == "cv"]
    tx = [item for item in bundle["evidence"] if item["source"]["source_doc"] == "transcript"]
    cv_text = " ".join(item["claim"].lower() for item in cv)
    tx_text = " ".join(item["claim"].lower() for item in tx)
    leadership = any(cv_text.startswith(prefix) or f" {prefix}" in cv_text for prefix in ("led ", "owned ", "lead "))
    reduced_scope = any(phrase in tx_text for phrase in ("contributed implementation", "shared the final ownership", "staff engineer owned", "parts of the rollout"))
    if leadership and reduced_scope:
        ids = [item["evidence_id"] for item in cv + tx if item["evidence_id"]]
        return _finding("conflicting_evidence", "block", "Resume ownership language is narrower or inconsistent with the interview account; recruiter review is required.", ids)
    return None


def _assessment_findings(assessment: dict[str, Any] | None, as_of: date) -> list[dict[str, Any]]:
    if assessment is None:
        return [_finding("missing_evidence", "block", "No assessment is present for this packet.")]
    assessed = date.fromisoformat(assessment["date"])
    if assessed < as_of - timedelta(days=180):
        return [_finding("stale_evidence", "block", f"Assessment dated {assessment['date']} is older than the 180-day freshness policy.")]
    return []


def validate_v2(bundle: dict[str, Any], assessment: dict[str, Any] | None, as_of: date) -> dict[str, Any]:
    findings: list[dict[str, Any]] = []
    conflict = _conflict(bundle)
    if conflict:
        findings.append(conflict)
    findings.extend(_assessment_findings(assessment, as_of))
    ambiguous = [item for item in bundle["evidence"] if item["evidence_quality"] == "ambiguous"]
    if ambiguous:
        findings.append(_finding("ambiguous_evidence", "review", "Some evidence describes scope or ownership ambiguously and needs reviewer clarification.", [item["evidence_id"] for item in ambiguous]))
    uncorroborated = [item for item in bundle["evidence"] if item["evidence_quality"] == "uncorroborated" or not item["corroboration"]]
    if uncorroborated:
        findings.append(_finding("uncorroborated_evidence", "review", "Some claims are not corroborated across the available documents.", [item["evidence_id"] for item in uncorroborated]))
    return {
        "profile_id": bundle["profile_id"],
        "role_family": bundle["role_family"],
        "coverage": _coverage(bundle["requirements"], bundle["evidence"]),
        "findings": findings,
        "blocking": any(f["severity"] == "block" for f in findings),
    }
