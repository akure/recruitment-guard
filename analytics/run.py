from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analytics.metrics import aggregate_metrics, render_metrics
from ops.events import make_event

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data_ops'
OUT = ROOT / 'analytics'


def run() -> dict:
    manifest = json.loads((DATA / 'MANIFEST.json').read_text())
    records = []
    review_conditions = {'contradiction', 'missing_consent', 'stale_assessment', 'unsupported_claim', 'work_mode_mismatch'}
    for packet in manifest['packets']:
        packet_id = packet['packet_id']
        folder = DATA / f"packet_{packet_id}"
        consent = json.loads((folder / 'consent.json').read_text())
        ground_truth = json.loads((folder / 'ground_truth.json').read_text())
        base = datetime(2026, 8, 30, 9, 0, tzinfo=timezone.utc) + timedelta(minutes=int(packet_id))
        events = [make_event(packet_id, 'packet_ingested', 'system', {'source': 'folder'}, (base).isoformat().replace('+00:00', 'Z'))]
        consent_type = 'consent_recorded' if consent['status'] == 'granted' else 'consent_withdrawn'
        events.append(make_event(packet_id, consent_type, 'system', {'purpose': consent['purpose'], 'scope_count': len(consent['scope'])}, (base + timedelta(minutes=1)).isoformat().replace('+00:00', 'Z')))
        if packet['condition'] in review_conditions:
            events.append(make_event(packet_id, 'review_requested', 'system', {'finding_count': 1, 'condition': packet['condition']}, (base + timedelta(minutes=5)).isoformat().replace('+00:00', 'Z')))
            events.append(make_event(packet_id, 'finding_resolved', 'recruiter', {'review_id': f"review-{packet_id}", 'condition': packet['condition']}, (base + timedelta(minutes=15)).isoformat().replace('+00:00', 'Z')))
        rework = 1 if packet['condition'] in {'unsupported_claim', 'work_mode_mismatch'} else 0
        events.append(make_event(packet_id, 'brief_exported', 'recruiter', {'rework_count': rework, 'evidence_only': True}, (base + timedelta(minutes=18)).isoformat().replace('+00:00', 'Z')))
        records.append({'packet_id': packet_id, 'profile_id': packet['profile_id'], 'role_family': packet['role_family'], 'condition': packet['condition'], 'consent_status': consent['status'], 'synthetic_only': True, 'ground_truth_expected_blocking': ground_truth['expected_blocking'], 'events': events})
    result = aggregate_metrics(records)
    (OUT / 'ops_results.json').write_text(json.dumps({'records': records, 'summary': result}, indent=2) + '\n')
    (OUT / 'ops_metrics.md').write_text(render_metrics(result))
    return result


if __name__ == '__main__':
    result = run()
    print(json.dumps(result['metrics'], indent=2))
