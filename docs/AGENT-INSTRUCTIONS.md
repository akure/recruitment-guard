# Agent instructions and design contract

This document indexes the instructions that shape each runtime path. The complete executable source remains in the repository; this page makes the submission auditable without requiring judges to infer prompts from imports.

## Baseline summarizer

Source: [`baseline/run.py`](../baseline/run.py), constant `PROMPT`.

> Summarize this synthetic Backend Engineer candidate packet for a hiring manager. Describe relevant experience and evidence from the CV and interview transcript. Do not make a hire/no-hire recommendation, score, or ranking. If sources disagree, write a coherent summary without adding facts not present in the packet.

The baseline intentionally has no extraction, contradiction validator, freshness check, or human checkpoint. This is the fair simple comparison path.

## Guarded extraction agent

Source: [`extraction/extract.py`](../extraction/extract.py), constant `PROMPT`.

> Extract only material facts matching one of these subject prefixes: `team_size_<project_slug>`, `ownership_<project_slug>`, `skill_claim_<skill_slug>`, `skill_demonstrated_<skill_slug>`, `tenure_<company_slug>`. Quote `source_span` verbatim from the document. Do not infer, paraphrase, or force-fit. Return JSON with `source_doc`, `packet_id`, and `facts[]`.

The structured response is checked for packet/document identity, allowed subject prefixes, verbatim source spans, and offsets. In live mode, an incorrect model offset is repaired only when the quoted span has one exact match; duplicate or missing matches fail closed.

## Deterministic guarded validator

Sources: [`validator/validate.py`](../validator/validate.py), [`validator/v2_validate.py`](../validator/v2_validate.py).

The validator compares only matching explicit subjects, checks missing and stale assessment evidence, identifies contradictions and ambiguity, and assigns a blocking state before brief generation. It does not infer personality, protected traits, deception, immigration status, productivity, suitability, or hireability.

## Human checkpoint and exporter

Sources: [`checkpoint/`](../checkpoint/), [`workflow/review.py`](../workflow/review.py), [`checkpoint/v2_brief.py`](../checkpoint/v2_brief.py).

Blocking findings create an open review item with owner, due date, evidence IDs, and status. A recruiter must provide an attributable resolution note before finalization. Withdrawn or inactive consent cannot be overridden. Exported briefs contain source citations, requirement coverage, unresolved questions, consent metadata, and an evidence-only disclaimer; they contain no decision field.

## v2.1 Evidence Operations operator path

Sources: [`workflow/importer.py`](../workflow/importer.py), [`workflow/run.py`](../workflow/run.py).

The operator can provide a packet directory, a directory of packets, or a CSV/JSON manifest. The workflow normalizes ingestion into typed events, validates consent, runs the guarded path, creates a review queue when necessary, and writes Markdown/JSON artifacts. It is deliberately integration-neutral and performs no ATS write-back or external consequential action.

## Model configuration

The live path uses the OpenAI-compatible client with `RECRUITMENT_GUARD_MODEL` (default `gpt-5-mini`), `RECRUITMENT_GUARD_TIMEOUT` (default `45` seconds), and one retry. The deterministic mock path is the default for reproduction and CI; it requires no credentials and is the source of the committed reproducible benchmark metrics.
