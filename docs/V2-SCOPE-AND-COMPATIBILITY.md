# V2 scope and V1 compatibility contract

## Scope

V2 expands RecruitmentGuard from one clean Backend Engineer benchmark into a configurable evidence-review workflow for three hiring contexts: startup, enterprise, and small team. The benchmark uses realistic but entirely fictional job descriptions, resumes, transcripts, assessments, and ground-truth annotations.

V2 is still **not** an applicant-ranking or hiring-decision system. It does not emit hire/no-hire recommendations, scores, rankings, protected-trait inferences, or automated actions. Profile configuration changes the evidence requested and the gaps described; it does not change that safety boundary.

## V1 preservation

| V1 asset or behavior | V2 compatibility rule |
|---|---|
| `data/packet_01..12/` | Never mutate or regenerate. V2 uses `data_v2/`. |
| V1 packet layout | Remains readable by the V1 baseline, extraction, validator, and evaluation commands. |
| V1 extracted-fact schema | Remains valid and unchanged. V2 adds separate schemas rather than silently changing required fields. |
| V1 brief disclaimer | Remains mandatory in all V2 briefs. |
| V1 deterministic block gate | Remains the safety boundary. V2 may add deterministic finding types but may not delegate blocking to free-form model judgment. |
| V1 release | `v1.0.0` remains the reproducibility baseline. V2 releases are tagged separately. |

## V2 packet contract

Each V2 packet contains:

```text
data_v2/packet_NNN/
  profile.json
  jd.md
  cv.md
  transcript.md
  assessment.json       # optional
  ground_truth.json     # benchmark-only, not candidate-facing
```

`profile.json` points to one of the versioned hiring-context profiles. `ground_truth.json` describes planted benchmark conditions and is used only by evaluation code; it is never passed to the extraction or briefing path.

## Initial benchmark coverage

The first generator produces 12 packets covering three profiles and four role families: backend/platform, product engineering, data/ML infrastructure, and security/reliability. Packets include clean evidence, contradiction, missing evidence, stale evidence, ambiguous evidence, timeline inconsistency, and hard-negative variants.

The benchmark is deliberately deterministic. Re-running `scripts/generate_data_v2.py` replaces only `data_v2/` and produces the same fictional names, documents, profile assignments, and annotations.
