# Evaluation metrics

Both paths were run on the identical 12 synthetic candidate packets. Values below are produced by `eval/run.py`; they are not estimates.

| Metric                          | Baseline | Guarded | Change |
|----------------------------------|----------|---------|--------|
| Planted cases surfaced (of 3)    | 0 | 3 | +3 |
| False positives (of 9 clean)     | n/a | 0 | — |
| Avg. time per packet             | 0.000002 | 0.000988 | +0.000986 |
| Avg. token cost per packet       | 0 | 0 | +0 |

The baseline is the existing single-prompt summarizer. The guarded path is the existing extraction → deterministic validation → checkpoint pipeline. Mock mode uses zero model tokens and is intended for deterministic local verification; live-mode token usage is recorded when the API-backed paths are run.
