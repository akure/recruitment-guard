# Changelog

This changelog records each sprint and meaningful behavior change as it happens. Evaluation claims will be added only after they are produced by the reproducible evaluation harness.

| Stage | What you tried and why | Evidence | Decision / Learning |
|---|---|---|---|
| Sprint 0 — Scope lock | Added the approved problem brief for a guarded candidate-evidence workflow. Fixed the role, synthetic 12-packet evaluation design, baseline-vs-guarded comparison, and no-hire/no-score constraint before implementation. | Not yet measured; implementation and evaluation have not started. | Approved foundation. Preserve the fixed scope and do not add ranking, real candidate data, ATS integrations, or automated consequential decisions. |

## Changelog discipline

Every sprint or meaningful behavior change must append a row in the same change set before the next implementation step. A meaningful change includes dataset content, extraction taxonomy or prompt, validator logic, checkpoint behavior, brief template, evaluation logic, or trajectory logging. Pure refactors that do not change behavior may be noted without a full evaluation rerun.

Every measured result must link to the generated `eval/metrics.md` output. Do not estimate or backfill metrics. If an experiment produces no metric movement, record the null result and the resulting decision.
