# V2 cross-context evaluation metrics

Both paths were evaluated on the V2 synthetic benchmark. Metrics are generated from per-packet guarded outputs and ground-truth conditions; they are not hiring recommendations.

## Overall metrics

| Metric | Measured value |
|---|---:|
| Finding recall | 5/5 (100.00%) |
| Blocking false positives on clean/hard-negative/ambiguous controls | 0 |
| Citation fidelity | 100.00% |

## Per-profile metrics

| Hiring profile | Packets | Expected findings surfaced | Finding recall | Review packets | Review rate | Citation fidelity |
|---|---:|---:|---:|---:|---:|---:|
| enterprise | 4 | 1/1 | 100.00% | 1 | 25.00% | 100.00% |
| small_team | 4 | 3/3 | 100.00% | 3 | 75.00% | 100.00% |
| startup | 4 | 1/1 | 100.00% | 1 | 25.00% | 100.00% |

## Reviewer burden

| Measure | Value |
|---|---:|
| Packets requiring review | 5 |
| Review rate | 41.67% |
| Blocking findings | 5 |
| Average reviewer questions per packet | 2.00 |
| Average blocking findings per review packet | 1.00 |

This evaluation measures evidence surfacing and review workload only. It is evidence only and contains no candidate score, ranking, or hire/no-hire recommendation.
