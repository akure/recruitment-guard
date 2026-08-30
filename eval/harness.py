from __future__ import annotations

from statistics import mean
from typing import Iterable

PLANTED_PACKETS = {"01", "02", "03"}
CLEAN_PACKETS = {f"{number:02d}" for number in range(4, 13)}


def evaluate_records(records: Iterable[dict]) -> dict:
    records = list(records)
    packet_ids = {record["packet_id"] for record in records}
    expected = PLANTED_PACKETS | CLEAN_PACKETS
    if packet_ids != expected:
        raise ValueError(f"evaluation must contain packets 01-12; got {sorted(packet_ids)}")

    planted_guarded = sum(
        bool(record.get("guarded_findings")) for record in records if record["packet_id"] in PLANTED_PACKETS
    )
    planted_baseline = sum(
        bool(record.get("baseline_surface")) for record in records if record["packet_id"] in PLANTED_PACKETS
    )
    false_positives = sum(
        bool(record.get("guarded_findings")) for record in records if record["packet_id"] in CLEAN_PACKETS
    )
    return {
        "baseline_planted_surfaced": planted_baseline,
        "guarded_planted_surfaced": planted_guarded,
        "guarded_false_positives": false_positives,
        "baseline_avg_time_seconds": mean(record.get("baseline_time_seconds", 0) for record in records),
        "guarded_avg_time_seconds": mean(record.get("guarded_time_seconds", 0) for record in records),
        "baseline_avg_tokens": mean(record.get("baseline_tokens", 0) for record in records),
        "guarded_avg_tokens": mean(record.get("guarded_tokens", 0) for record in records),
    }


def _number(value: float | int) -> str:
    if isinstance(value, int) or float(value).is_integer():
        return str(int(value))
    return f"{value:.6f}"


def _delta(left: float | int, right: float | int) -> str:
    value = right - left
    return f"+{_number(value)}" if value >= 0 else _number(value)


def render_metrics(summary: dict) -> str:
    baseline_time = summary["baseline_avg_time_seconds"]
    guarded_time = summary["guarded_avg_time_seconds"]
    baseline_tokens = summary["baseline_avg_tokens"]
    guarded_tokens = summary["guarded_avg_tokens"]
    return "\n".join([
        "# Evaluation metrics",
        "",
        "Both paths were run on the identical 12 synthetic candidate packets. Values below are produced by `eval/run.py`; they are not estimates.",
        "",
        "| Metric                          | Baseline | Guarded | Change |",
        "|----------------------------------|----------|---------|--------|",
        f"| Planted cases surfaced (of 3)    | {summary['baseline_planted_surfaced']} | {summary['guarded_planted_surfaced']} | {_delta(summary['baseline_planted_surfaced'], summary['guarded_planted_surfaced'])} |",
        f"| False positives (of 9 clean)     | n/a | {summary['guarded_false_positives']} | — |",
        f"| Avg. time per packet             | {_number(baseline_time)} | {_number(guarded_time)} | {_delta(baseline_time, guarded_time)} |",
        f"| Avg. token cost per packet       | {_number(baseline_tokens)} | {_number(guarded_tokens)} | {_delta(baseline_tokens, guarded_tokens)} |",
        "",
        "The baseline is the existing single-prompt summarizer. The guarded path is the existing extraction → deterministic validation → checkpoint pipeline. Mock mode uses zero model tokens and is intended for deterministic local verification; live-mode token usage is recorded when the API-backed paths are run.",
        "",
    ])
