from __future__ import annotations

from collections import Counter, defaultdict
from statistics import mean
from typing import Any

EXPECTED = {
    "contradiction": "conflicting_evidence",
    "missing_assessment": "missing_evidence",
    "stale_assessment": "stale_evidence",
    "timeline_inconsistency": "timeline_inconsistency",
}


def _blocking(record: dict[str, Any]) -> list[dict[str, Any]]:
    return [finding for finding in record.get("findings", []) if finding.get("severity") == "block"]


def evaluate_v2_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    if not records:
        raise ValueError("records must not be empty")
    expected_total = 0
    expected_surfaced = 0
    blocking_false_positives = 0
    per_profile: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        expected = EXPECTED.get(record["condition"])
        finding_types = {finding["type"] for finding in record.get("findings", [])}
        if expected:
            expected_total += 1
            expected_surfaced += int(expected in finding_types)
        elif record["condition"] in {"clean", "hard_negative", "ambiguous_scope"}:
            blocking_false_positives += int(bool(_blocking(record)))
        per_profile[record["profile_id"]].append(record)

    burden = {
        "packets_requiring_review": sum(record.get("state") == "pending_review" for record in records),
        "review_rate": sum(record.get("state") == "pending_review" for record in records) / len(records),
        "blocking_findings": sum(len(_blocking(record)) for record in records),
        "avg_review_questions_per_packet": mean(record.get("review_questions", 0) for record in records),
    }
    review_packets = [record for record in records if record.get("state") == "pending_review"]
    burden["avg_blocking_findings_per_review_packet"] = (burden["blocking_findings"] / len(review_packets)) if review_packets else 0.0

    profile_summary = {}
    for profile_id, profile_records in sorted(per_profile.items()):
        profile_expected = sum(record["condition"] in EXPECTED for record in profile_records)
        profile_surfaced = sum(EXPECTED.get(record["condition"]) in {f["type"] for f in record.get("findings", [])} for record in profile_records if record["condition"] in EXPECTED)
        profile_summary[profile_id] = {
            "packets": len(profile_records),
            "expected_findings_surfaced": profile_surfaced,
            "expected_findings_total": profile_expected,
            "finding_recall": profile_surfaced / profile_expected if profile_expected else None,
            "review_packets": sum(record.get("state") == "pending_review" for record in profile_records),
            "review_rate": sum(record.get("state") == "pending_review" for record in profile_records) / len(profile_records),
            "citation_fidelity": mean(record.get("citation_fidelity", 0.0) for record in profile_records),
        }
    return {
        "context_counts": dict(sorted(Counter(record["profile_id"] for record in records).items())),
        "expected_findings_surfaced": expected_surfaced,
        "expected_findings_total": expected_total,
        "finding_recall": expected_surfaced / expected_total if expected_total else 0.0,
        "blocking_false_positives": blocking_false_positives,
        "citation_fidelity": mean(record.get("citation_fidelity", 0.0) for record in records),
        "reviewer_burden": burden,
        "per_profile": profile_summary,
    }


def render_v2_metrics(summary: dict[str, Any]) -> str:
    burden = summary["reviewer_burden"]
    lines = [
        "# V2 cross-context evaluation metrics",
        "",
        "Both paths were evaluated on the V2 synthetic benchmark. Metrics are generated from per-packet guarded outputs and ground-truth conditions; they are not hiring recommendations.",
        "",
        "## Overall metrics",
        "",
        "| Metric | Measured value |",
        "|---|---:|",
        f"| Finding recall | {summary['expected_findings_surfaced']}/{summary['expected_findings_total']} ({summary['finding_recall']:.2%}) |",
        f"| Blocking false positives on clean/hard-negative/ambiguous controls | {summary['blocking_false_positives']} |",
        f"| Citation fidelity | {summary['citation_fidelity']:.2%} |",
        "",
        "## Per-profile metrics",
        "",
        "| Hiring profile | Packets | Expected findings surfaced | Finding recall | Review packets | Review rate | Citation fidelity |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for profile_id, metrics in sorted(summary["per_profile"].items()):
        recall = "n/a" if metrics["finding_recall"] is None else f"{metrics['finding_recall']:.2%}"
        lines.append(f"| {profile_id} | {metrics['packets']} | {metrics['expected_findings_surfaced']}/{metrics['expected_findings_total']} | {recall} | {metrics['review_packets']} | {metrics['review_rate']:.2%} | {metrics['citation_fidelity']:.2%} |")
    lines.extend([
        "",
        "## Reviewer burden",
        "",
        "| Measure | Value |",
        "|---|---:|",
        f"| Packets requiring review | {burden['packets_requiring_review']} |",
        f"| Review rate | {burden['review_rate']:.2%} |",
        f"| Blocking findings | {burden['blocking_findings']} |",
        f"| Average reviewer questions per packet | {burden['avg_review_questions_per_packet']:.2f} |",
        f"| Average blocking findings per review packet | {burden['avg_blocking_findings_per_review_packet']:.2f} |",
        "",
        "This evaluation measures evidence surfacing and review workload only. It is evidence only and contains no candidate score, ranking, or hire/no-hire recommendation.",
        "",
    ])
    return "\n".join(lines)
