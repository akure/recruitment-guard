from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from statistics import median
from typing import Any


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def _packet_metrics(record: dict[str, Any]) -> dict[str, Any]:
    events = record.get('events', [])
    review_events = [e for e in events if e['event_type'] == 'review_requested']
    resolution_events = [e for e in events if e['event_type'] == 'finding_resolved']
    export_events = [e for e in events if e['event_type'] == 'brief_exported']
    review_minutes = None
    if review_events:
        start = _dt(review_events[0]['occurred_at'])
        end_events = resolution_events or export_events
        if end_events:
            review_minutes = round((_dt(end_events[0]['occurred_at']) - start).total_seconds() / 60, 2)
    finding_count = sum(int(e.get('payload', {}).get('finding_count', 0)) for e in review_events)
    rework_count = sum(int(e.get('payload', {}).get('rework_count', 0)) for e in events)
    return {
        'packet_id': record['packet_id'],
        'profile_id': record['profile_id'],
        'review_required': bool(review_events),
        'review_minutes': review_minutes,
        'finding_count': finding_count,
        'rework_count': rework_count,
        'consent_complete': record.get('consent_status') == 'granted',
        'exported': bool(export_events),
    }


def _aggregate_rows(rows: list[dict[str, Any]]) -> dict[str, Any]:
    review_times = [r['review_minutes'] for r in rows if r['review_minutes'] is not None]
    return {
        'packet_count': len(rows),
        'packets_requiring_review': sum(r['review_required'] for r in rows),
        'review_rate': round(sum(r['review_required'] for r in rows) / len(rows), 4) if rows else 0.0,
        'median_review_minutes': float(median(review_times)) if review_times else 0.0,
        'average_review_minutes': round(sum(review_times) / len(review_times), 2) if review_times else 0.0,
        'total_findings_reviewed': sum(r['finding_count'] for r in rows),
        'rework_events': sum(r['rework_count'] for r in rows),
        'consent_completeness_rate': round(sum(r['consent_complete'] for r in rows) / len(rows), 4) if rows else 0.0,
        'brief_export_rate': round(sum(r['exported'] for r in rows) / len(rows), 4) if rows else 0.0,
    }


def aggregate_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    rows = [_packet_metrics(record) for record in records]
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row['profile_id']].append(row)
    return {
        'schema_version': 'ops.metrics.v1',
        'benchmark_id': 'evidence-operations-24',
        'packet_count': len(rows),
        'metrics': _aggregate_rows(rows),
        'by_profile': [dict(profile_id=profile, **_aggregate_rows(grouped[profile])) for profile in sorted(grouped)],
        'packet_rows': rows,
        'safety_boundary': 'Operational workflow metrics only; no candidate quality, suitability, ranking, or hiring outcome is inferred.',
    }


def render_metrics(result: dict[str, Any]) -> str:
    m = result['metrics']
    lines = [
        '# Evidence Operations metrics', '',
        '> Operational workflow metrics only; no candidate quality, suitability, ranking, or hiring outcome is inferred.', '',
        f"Benchmark: `{result['benchmark_id']}`",
        f"Packets: **{result['packet_count']}**",
        '',
        '| Metric | Measured value |',
        '|---|---:|',
        f"| Packets requiring review | {m['packets_requiring_review']}/{m['packet_count']} ({m['review_rate']:.2%}) |",
        f"| Median review time | {m['median_review_minutes']:.2f} minutes |",
        f"| Average review time | {m['average_review_minutes']:.2f} minutes |",
        f"| Findings reviewed | {m['total_findings_reviewed']} |",
        f"| Rework events | {m['rework_events']} |",
        f"| Consent completeness | {m['consent_completeness_rate']:.2%} |",
        f"| Brief export rate | {m['brief_export_rate']:.2%} |",
        '',
        '## By hiring profile', '',
        '| Profile | Packets | Review rate | Median review min | Consent completeness | Rework events |',
        '|---|---:|---:|---:|---:|---:|',
    ]
    for row in result['by_profile']:
        lines.append(f"| {row['profile_id']} | {row['packet_count']} | {row['review_rate']:.2%} | {row['median_review_minutes']:.2f} | {row['consent_completeness_rate']:.2%} | {row['rework_events']} |")
    lines += ['', '## Interpretation boundary', '', 'These measurements describe workflow load, consent completeness, and evidence-review operations. They are not candidate quality metrics and must not be used as a proxy for candidate suitability or hiring outcomes.']
    return '\n'.join(lines) + '\n'
