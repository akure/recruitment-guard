# Representative Agent Trajectories

These are annotated runtime trajectories for the agents in the submitted solution. They are derived from the committed prompts, deterministic traces, checkpoint artifacts, and the live-evaluation failure recorded in `CHANGELOG.md`. The trajectories intentionally show the feedback loop and the point where human review is required.

## Trajectory A — Simple baseline summarizer

| Step | Agent instruction/action | Tool or system response | Feedback and next step |
|---|---|---|---|
| 1 | System prompt: “Summarize this synthetic Backend Engineer candidate packet for a hiring manager. Describe relevant experience and evidence from the CV and interview transcript. Do not make a hire/no-hire recommendation, score, or ranking.” | `baseline/run.py` loads the CV and transcript and calls one summarization path. | The baseline has context but no structured cross-document comparison. |
| 2 | Agent receives both documents in one user message. | It returns a coherent Markdown summary and the mandatory evidence-only disclaimer. | Because the output is narrative-only, contradictions can remain smooth prose. |
| 3 | Evaluation scores only the summary section, excluding the disclaimer. | On the identical 12-packet V1 benchmark, the baseline surfaced `0/3` planted cases. | The observed miss justified structured extraction and deterministic verification. |

Prompt source: `baseline/run.py`. Reproduction command: `python3 baseline/run.py data/packet_04 --mock`.

## Trajectory B — Guarded extraction, validation, and checkpoint

| Step | Agent instruction/action | Tool or system response | Feedback and next step |
|---|---|---|---|
| 1 | Extraction prompt restricts subjects to `team_size_*`, `ownership_*`, `skill_claim_*`, `skill_demonstrated_*`, and `tenure_*`; it requires verbatim source spans and offsets. | `extraction/extract.py` returns structured CV and transcript facts. In mock mode, token usage is `0`; in live mode, usage is recorded. | Fixed taxonomy preserves comparability and prevents free-form inference. |
| 2 | Deterministic validator compares matching subjects and checks assessment freshness. | For packet `03`, it emits `missing_evidence` with `severity: block`; for packet `04`, it records a clean finalization path. | A blocking finding cannot be converted into a final brief automatically. |
| 3 | The checkpoint writes a pending artifact and trajectory instead of a brief. | `trajectories/packet_03.json` records `stage_1_extraction`, `stage_2_validation`, `stage_3_pause`, and no `stage_4_final_brief`. | The next action is explicitly delegated to the recruiter. |
| 4 | Recruiter resolves the finding with a note. | `checkpoint.resolve` records the actor and note; `checkpoint.finalize` permits output only when every blocking finding is resolved. | Human review is a hard gate, not a warning. |
| 5 | Evidence-bound brief renderer writes the final Markdown brief. | The brief contains cited evidence, gaps, finding sections, reviewer questions, and the unconditional no-recommendation disclaimer. | The human remains responsible for the hiring decision outside the system. |

Prompt source: `extraction/extract.py`; deterministic control sources: `validator/validate.py`, `checkpoint/`, and `guarded/runner.py`. Representative artifacts: `trajectories/packet_03.json` and `trajectories/packet_04.json`.

## Trajectory C — v2.1 Evidence Operations workflow

| Step | Operator/agent action | Tool or system response | Feedback and next step |
|---|---|---|---|
| 1 | Operator runs `python3 -m workflow.run data_ops/packet_001 --output-root /tmp/rg-demo-clean --as-of 2026-08-30 --owner recruiter`. | Folder importer normalizes the packet, validates consent, emits `packet_ingested`, and runs profile-aware extraction and validation. | Clean evidence is eligible for export. |
| 2 | Workflow writes `brief.md` and `audit.json`. | The audit contains consent metadata, source files, event history, validation output, and no decision field. | The reviewer receives a traceable handoff packet. |
| 3 | Operator runs the same workflow on stale-assessment packet `004` with `--due-at 2026-09-02T17:00:00Z`. | The workflow creates an open review item with owner and due date, emits `review_requested`, and withholds the brief. | The reviewer must resolve the finding before finalization. |
| 4 | Recruiter runs `workflow.run --resolve-packet 004 --actor recruiter --resolution-note ...`. | The review item becomes resolved, `finding_resolved` and `brief_exported` events are recorded, and the brief is written. | The output is complete only after attributable human review. |
| 5 | Recruiter attempts the same override on withdrawn-consent packet `003`. | The workflow rejects the override with `ValueError`; no brief is emitted. | Consent withdrawal is a permanent hard stop. |

Workflow source: `workflow/importer.py`, `workflow/run.py`, and `workflow/review.py`. The complete clean-checkout path is in `scripts/verify_clean_checkout.sh`.

## Trajectory D — Live-model failure and safe retry

| Step | Agent/system action | Tool or system response | Feedback and next step |
|---|---|---|---|
| 1 | Run `RECRUITMENT_GUARD_MODEL=gpt-5-mini python3 eval/run.py --live --output-root eval/live` on the same 12 V1 packets used by the mock comparison. | The model returned a verbatim citation with an incorrect character offset on the first guarded packet. | The provenance validator stopped the run; no invalid evidence reached a brief. |
| 2 | Engineering feedback identifies the exact failure: correct text, incorrect offset. | The extraction validator is hardened to repair offsets only when the quoted span is an exact unique substring; duplicate or missing spans still fail closed. Provider calls receive bounded timeout and retry settings. | The repair improves robustness without trusting model-supplied positions. |
| 3 | Regression tests cover unique-span repair and duplicate-span rejection. | The full suite passes `45/45`. | Live quality remains unclaimed until all same-case packets complete successfully; deterministic mock evaluation remains the reproducible gate. |

This failure is the central reliability lesson: **in consequential workflows, the best agent output is often a precisely cited reason to pause—not a confident recommendation.**

## What these trajectories demonstrate

The system uses one simple baseline and one guarded agent path rather than unnecessary multi-agent orchestration. The model proposes structured evidence; deterministic code verifies source fidelity and blocking conditions; and a human checkpoint controls finalization. The artifacts show both successful execution and safe failure, including the feedback, retry, and human-resolution boundaries that matter for a hiring workflow.
