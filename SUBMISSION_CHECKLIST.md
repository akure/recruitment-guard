# Submission checklist and self-score

## Required deliverables

| Deliverable | Location | Status |
|---|---|---|
| Solution code and running changelog | Repository source plus `CHANGELOG.md` | Present |
| Reproduction guide | `REPRODUCE.md` | Present |
| Solution video script | `video/SCRIPT.md` | Present |
| Representative agent trajectories | `trajectories/` | Present: packet 03 paused, packet 04 finalized |
| Measured evaluation | `eval/metrics.md`, `eval/results.json` | Present |

## Rubric self-check

| Criterion | Points | Honest assessment | Band |
|---|---:|---|---|
| Problem & User Value | 15 | The README names Priya and describes contradiction blindness and missing/stale evidence in a concrete recruiter workflow. | Strong |
| Agent Solution & Engineering | 30 | Structured extraction, deterministic validation, and a human checkpoint each map to a specific failure mode; memory, orchestration, and external actions are deliberately omitted. | Strong |
| End-to-End Quality | 20 | The brief has source-bound claims, flagged findings, gap handling, resolution notes, and an unconditional no-recommendation disclaimer. | Adequate-to-strong; the local mock path is intentionally minimal rather than UI-polished. |
| Measured Improvement | 15 | The same 12 packets feed both paths; the committed harness measured baseline `0/3`, guarded `3/3`, and `0/9` guarded false positives. | Strong for the deterministic mock evaluation; live-model quality remains unmeasured. |
| Reproducibility | 15 | `REPRODUCE.md` gives separate baseline, guarded, evaluation, and test commands and the repository contains synthetic data. | Strong for a credential-free clean checkout: the pushed repository was cloned fresh and baseline, guarded, evaluation, and tests all passed. An independent second-person run remains a useful additional check. |
| Hot Take / Insights | 5 | The changelog records the observed disclaimer-scoring failure and the extraction/heuristic fixes that followed. | Strong |

**Weakest criterion:** Reproducibility is the weakest remaining area only because an independent clean-checkout run has not been performed by a second person. The guide is credential-free and the local mock path is designed to make that verification straightforward.

## Ground-rules compliance

| Rule | Check | Status |
|---|---|---|
| 01 | Uses standard Python and an OpenAI-compatible optional dependency. | Pass |
| 02 | README identifies the project as a from-scope hackathon build and separates libraries from project code. | Pass |
| 03 | No scraped or third-party candidate data; dependency and API usage are explicitly documented. | Pass |
| 04 | No external consequential action exists; finalization is locally gated by recruiter resolution. | Pass |
| 05 | No hire/no-hire output, score, or ranking; human review is required for blocking findings. | Pass |
| 06 | Synthetic fictional candidates only; no bias-freedom or legal-compliance claims. | Pass |
| 07 | All demo/evaluation data is synthetic and included in the repository. | Pass |
| 08 | No `.env`, API keys, or credentials are committed. | Pass after repository grep |
| 09 | README metrics match committed `eval/metrics.md` and `eval/results.json`; changelog records the same run. | Pass |
| 10 | `REPRODUCE.md` supplies credential-free commands and expected outputs. | Pass |

Any future change to prompts, taxonomy, validator logic, checkpoint behavior, evaluation logic, or trajectory logging requires a same-change-set changelog entry and a fresh relevant verification run.
