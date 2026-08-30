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

## 1:00–2:45 — Guarded execution from start to finish

Run the guarded workflow on packet 03:

```bash
python3 -m guarded.runner 03 --mock
```

Show that the runner extracts structured facts, validates the packet, writes `pending_review/packet_03.json`, and does not write a final brief because the assessment is missing. Open the trajectory and show `stage_1_extraction`, the `missing_evidence` finding, and `stage_3_pause`.

Resolve the finding as the recruiter:

```bash
python3 -m checkpoint.resolve 03 --finding c1 \
  --note "Recruiter acknowledged that no assessment was on file." \
  --pending-dir pending_review
python3 -m checkpoint.finalize 03 --extraction-dir extraction/output \
  --pending-dir pending_review --brief-dir briefs
```

Open the finalized brief and show the evidence summary, gap section, resolution note, and mandatory evidence-only disclaimer. Emphasize that finalization was unreachable until the human resolution existed.

Optionally show packet 01’s trajectory to demonstrate a contradiction finding sourced from CV/transcript spans.

## 2:45–3:25 — Architecture and safety boundary

Show the README architecture diagram. Explain the sequential path: extraction, deterministic validator, checkpoint, evidence-bound brief, trajectory log. Highlight that the validator owns the block/no-block branch and that model classification is isolated to a narrow claim-comparison boundary. Confirm that all data is synthetic and no ATS, email, ranking, or recommendation action is connected.

## 3:25–3:55 — Measured comparison

Run or open the committed result:

```bash
python3 eval/run.py
cat eval/metrics.md
```

Show the exact table: baseline surfaced `0/3` planted cases; guarded surfaced `3/3`; guarded false positives were `0/9` clean controls. Explain that this is the deterministic mock-mode measurement, so token cost is zero and live API token usage is not being claimed.

## 3:55–4:30 — Changelog and insight

Open `CHANGELOG.md`. Show that the first evaluation attempt exposed a baseline-scoring bug: the mandatory safety disclaimer was being counted as a finding. The evaluator was corrected to score only the summary section, then rerun. Close with the insight: **evaluation must score output semantics rather than boilerplate safety text, and a fixed extraction taxonomy must preserve comparability without silently broadening structure.**
