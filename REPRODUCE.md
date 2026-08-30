# Reproduce RecruitmentGuard

This guide is written for a stranger starting from a clean checkout. The repository contains only synthetic candidate packets and uses a deterministic local mock mode by default, so the main result requires no credentials or external service.

## Requirements

Use Python 3.11 or newer. The deterministic paths use only the Python standard library. The optional API-backed baseline and extraction paths use the dependency in `requirements.txt` and require `OPENAI_API_KEY` and `OPENAI_API_BASE`; those credentials are not needed for the reproducible mock result.

```bash
git clone https://github.com/akure/recruitment-guard.git
cd recruitment-guard
python3 --version
python3 -m pip install -r requirements.txt
```

The V1 dataset is already included under `data/`. It is synthetic, fictional, and frozen at dataset version `sprint-1`. V2.0 adds the additive `data_v2/` benchmark with 12 realistic-but-fictional packets across startup, enterprise, and small-team profiles. No private or real candidate data is required.

## 1. Run the baseline path

The baseline is a single-prompt summarizer with no extraction, deterministic validation, or checkpoint. The local mock command is credential-free:

```bash
python3 baseline/run.py data/packet_04 --mock
```

Expected output is a path such as `briefs/brief_baseline_04.md`. The output is a Markdown evidence summary and must contain the evidence-only disclaimer. A live API-backed run can omit `--mock` after the required environment variables are configured.

## 2. Run the guarded solution path

Run a clean packet through extraction, validation, finalization, and trajectory logging:

```bash
python3 -m guarded.runner 04 --mock
```

Expected output reports `state: finalized` and writes:

- `briefs/brief_guarded_04.md`
- `extraction/output/packet_04.json`
- `trajectories/packet_04.json`

Run the missing-assessment case to observe the human checkpoint:

```bash
python3 -m guarded.runner 03 --mock
```

Expected output reports `state: pending_review`, writes `pending_review/packet_03.json`, and does not write a guarded brief. The evaluator/recruiter resolves the finding explicitly:

```bash
python3 -m checkpoint.resolve 03 \
  --finding c1 \
  --note "Recruiter acknowledged that no assessment was on file." \
  --pending-dir pending_review
python3 -m checkpoint.finalize 03 \
  --extraction-dir extraction/output \
  --pending-dir pending_review \
  --brief-dir briefs
```

The final brief is written only after the resolution exists. Its trajectory is updated with `resolved_by: recruiter` and the resolution note.

## 3. Run the V2.0 profile-aware solution

Generate or verify the additive V2 benchmark, extract profile-aware evidence, and run the profile-aware checkpoint:

```bash
python3 scripts/generate_data_v2.py
python3 -m extraction.run_v2
python3 -m checkpoint.v2_runner
```

Expected behavior is that non-blocking packets write `briefs/v2/brief_v2_NNN.md`, while contradiction, missing-assessment, stale-assessment, and timeline-inconsistency packets write `pending_review/v2/packet_NNN.json` and do not write a final brief. The V2 brief includes profile context, supported evidence, requirement gaps, ambiguity/corroboration sections, exact citations, and reviewer questions.

## 4. Run the V2.0 cross-context evaluation

The V2 evaluation executes the profile-aware path over all 12 identical V2 packets and writes measured results:

```bash
python3 eval/run_v2.py
```

Expected files:

- `eval/v2_metrics.md` — overall and per-profile metrics plus reviewer burden.
- `eval/v2_results.json` — per-packet records and the summary used to produce the table.

The V2.0 release benchmark should reproduce:

| Metric | Result |
|---|---:|
| Finding recall | 5/5 — 100% |
| Blocking false positives | 0 |
| Citation fidelity | 100% |
| Packets requiring human review | 5/12 — 41.67% |

| Profile | Packets | Finding recall | Review rate |
|---|---:|---:|---:|
| startup | 4 | 1/1 — 100% | 25% |
| enterprise | 4 | 1/1 — 100% | 25% |
| small_team | 4 | 3/3 — 100% | 75% |

The metrics measure evidence surfacing and review workload only. They do not measure candidate quality or hiring outcomes.

## 5. Run the V1 evaluation

The evaluation executes both paths over the identical 12 packets and writes machine-generated results:

```bash
python3 eval/run.py
```

Expected files:

- `eval/metrics.md` — required comparison table.
- `eval/results.json` — per-packet records and the summary used to produce the table.

The current deterministic mock run should reproduce this qualitative result:

| Metric | Baseline | Guarded |
|---|---:|---:|
| Planted cases surfaced | 0/3 | 3/3 |
| False positives on clean controls | n/a | 0/9 |

The mock run reports zero model tokens because no external model call is made. Runtime is measured on the host and may vary slightly; the committed `eval/metrics.md` contains the run used for the submission checkpoint.

## 6. Run the tests

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q baseline checkpoint extraction eval guarded validator tests
```

Expected result is a passing test suite covering validator rules, checkpoint enforcement, runner state transitions, trajectory output, and evaluation scoring.

## Reproducibility boundaries

This project intentionally does not connect to an ATS, email system, or other consequential external service. It does not make a hire/no-hire decision, score, or ranking. The recruiter checkpoint is a real file-based approval gate in the local workflow, and all candidate packets are synthetic.
