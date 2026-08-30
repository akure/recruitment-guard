# Evidence Operations Layer

The Evidence Operations Layer is an additive, vendor-neutral foundation for teams that want to start with folders or exports and add ATS integrations later. It is designed for recruiters and hiring managers who need traceable review packets without a technical implementation project.

## Run the benchmark

```bash
python3 scripts/generate_ops_benchmark.py
python3 -m unittest discover -s tests -v
```

The generator creates `data_ops/` with 24 realistic-but-fictional packets: eight startup, eight enterprise, and eight small-team cases. Each profile covers four role families and eight conditions: clean, contradiction, missing consent, stale assessment, unsupported claim, work-mode mismatch, sponsorship routing, and hard negative.

Each packet includes a profile, JD, resume, transcript, consent record, assessment, and benchmark-only ground truth. The `ops.ingest` module deliberately excludes `ground_truth.json` from candidate-facing normalized source files so evaluation annotations cannot leak into workflow output.

## Canonical workflow contracts

`schemas/workflow_event.schema.json` defines attributable events for ingestion, extraction, validation, review requests, resolutions, consent changes, and brief exports. `schemas/consent_record.schema.json` requires a purpose, explicit scope, status, timestamp, retention period, and source.

The current Python foundations are:

| Module | Responsibility |
|---|---|
| `ops.ingest` | Normalize a folder packet without an ATS dependency |
| `ops.consent` | Validate purpose, scope, retention, timestamps, and active status |
| `ops.events` | Create typed, attributable, timestamped workflow events |
| `ops.review` | Create owned review items and record human resolutions |

## Integration ladder

Begin with a folder, CSV, or JSON export. The normalized packet model can later be populated by shared-folder adapters, email forwarding, read-only ATS APIs, or webhooks. The core review and evidence logic must remain independent of the source vendor.

Write-back to an ATS or other external system is intentionally not implemented in this milestone. Any future write-back must be least-privilege, explicitly confirmed by a human, and recorded as an audit event.

## Safety boundary

This benchmark contains no real candidate data. Work mode, sponsorship, authorization, and consent are represented as explicit workflow facts or candidate-provided statements. The system does not infer nationality, immigration status, personality, protected traits, deception probability, productivity, or cultural suitability. It does not rank candidates, score candidates, reject candidates, or make hire/no-hire recommendations.
