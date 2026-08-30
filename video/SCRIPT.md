# RecruitmentGuard solution video script

**Target duration:** 4 minutes 30 seconds maximum.

## 0:00–0:35 — Problem and user

Show the README problem section and introduce Priya, a recruiter closing a Backend Engineer role. Explain that the résumé, interview transcript, and assessment were created separately, so a smooth summary can hide contradictions or silently omit stale evidence. State the design boundary: the system presents evidence and pauses for human review; it never makes a hire/no-hire decision.

## 0:35–1:00 — Simple baseline

Run:

```bash
python3 baseline/run.py data/packet_01 --mock
```

Open the generated baseline brief. Point out that it creates a coherent summary from the CV and transcript but has no structured fact comparison, evidence-freshness check, or human checkpoint. Keep this section short.

## 1:00–2:45 — v2.1 PMF workflow from start to finish

Run the primary workflow on a clean packet:

```bash
python3 -m workflow.run data_ops/packet_001 \
  --output-root /tmp/rg-demo-clean \
  --as-of 2026-08-30 --owner recruiter
```

Open `packet_001/brief.md` and `audit.json`. Show exact source-bound evidence, requirement coverage, consent metadata, and the evidence-only disclaimer.

Now run a stale-assessment packet with a review deadline:

```bash
python3 -m workflow.run data_ops/packet_004 \
  --output-root /tmp/rg-demo-review \
  --as-of 2026-08-30 --owner recruiter \
  --due-at 2026-09-02T17:00:00Z
```

Show that the result is `pending_review`, the review item has an owner and due date, and no final brief exists. Resolve and resume it as the recruiter:

```bash
python3 -m workflow.run --output-root /tmp/rg-demo-review \
  --resolve-packet 004 --actor recruiter \
  --resolution-note "Reviewer confirmed the evidence context."
```

Open the resulting brief and audit record. Emphasize that the resolution and export events are attributable and that finalization was unreachable until the human resolution existed. Mention that withdrawn consent is a permanent hard stop.

## 2:45–3:25 — Architecture and safety boundary

Show the README architecture diagram and the v2.1 workflow command. Explain the sequential path: import, extraction, deterministic validator, review queue, human resolution, evidence-bound brief, audit log. Highlight that the validator owns the block/no-block branch and that a model never executes a consequential action. Confirm that all data is synthetic and no ATS, email, ranking, or recommendation action is connected.

## 3:25–3:55 — Measured comparison

Run or open the committed deterministic result:

```bash
python3 eval/run.py
cat eval/metrics.md
```

Show the exact table: baseline surfaced `0/3` planted cases; guarded surfaced `3/3`; guarded false positives were `0/9` clean controls. Explain that this is the reproducible mock-mode measurement. Then show the live evaluation command:

```bash
RECRUITMENT_GUARD_MODEL=gpt-5-mini python3 eval/run.py --live --output-root eval/live
```

State clearly that live quality and token cost are reported only when all 12 same-case requests complete successfully; the deterministic validator remains the safety gate.

## 3:55–4:30 — Changelog and insight

Open `CHANGELOG.md`. Show that the first evaluation attempt exposed a baseline-scoring bug: the mandatory safety disclaimer was being counted as a finding. Show the later live-model failure: the model quoted a valid span but supplied an incorrect offset, so the deterministic provenance gate stopped the run. The implementation now repairs only exact unique spans and fails closed on ambiguity.

Close with the insight: **in consequential workflows, the best agent output is often a precisely cited reason to pause—not a confident recommendation.** Reliability means making evidence traceable, surfacing uncertainty before synthesis, and preventing a review question from silently becoming a hiring decision.
