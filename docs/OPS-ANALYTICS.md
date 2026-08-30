# Operational analytics and reviewer burden

The Evidence Operations analytics layer measures workflow load, not candidate quality. It consumes typed workflow events and packet metadata, then aggregates review requests, resolution time, rework events, consent completeness, and export completion.

## Run the analytics

```bash
python3 analytics/run.py
```

The command writes:

- `analytics/ops_results.json` with per-packet event records and the summary envelope.
- `analytics/ops_metrics.md` with the overall and profile-level metrics tables.

## Measured V2.1 fixture results

The current run uses all 24 realistic-but-fictional benchmark packets. Review and resolution timestamps are deterministic workflow fixtures so the pipeline can be reproduced without a live recruiting team. They are not claims about actual human reviewer speed.

| Metric | Overall |
|---|---:|
| Packets | 24 |
| Packets requiring review | 15/24 — 62.50% |
| Median review time | 10.00 minutes |
| Average review time | 10.00 minutes |
| Findings reviewed | 15 |
| Rework events | 6 |
| Consent completeness | 87.50% |
| Brief export rate | 100.00% |

| Profile | Packets | Review rate | Median review time | Consent completeness | Rework events |
|---|---:|---:|---:|---:|---:|
| Startup | 8 | 62.50% | 10.00 minutes | 87.50% | 2 |
| Enterprise | 8 | 62.50% | 10.00 minutes | 87.50% | 2 |
| Small team | 8 | 62.50% | 10.00 minutes | 87.50% | 2 |

The equal profile rows are expected in this first balanced fixture because every profile receives the same eight conditions. A later benchmark should vary case mix and compare the results against observed reviewer timings from an approved pilot.

## Event contract

A packet normally produces `packet_ingested`, `consent_recorded` or `consent_withdrawn`, optional `review_requested`, optional `finding_resolved`, and `brief_exported` events. Each event has an actor type, timestamp, packet ID, event type, and payload. Review duration is measured from `review_requested` to the first `finding_resolved`; clean packets have no review duration.

## Safety and interpretation boundary

The analytics layer must not calculate candidate suitability, candidate quality, hireability, ranking, or hiring outcome. Consent completeness is a workflow-control metric, not a candidate attribute. Rework events measure process friction, not candidate weakness. Sponsorship, work mode, and authorization events are routed as explicit workflow facts and are not converted into eligibility or suitability judgments.
