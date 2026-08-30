# RecruitmentGuard: PMF analysis and next-sprint plan

## Executive conclusion

RecruitmentGuard should not compete head-on with ATS platforms on sourcing, ranking, or automated screening. Those categories are already crowded, and the highest-risk features are also the least compatible with the project’s human-review and evidence-only boundary. The strongest wedge is an **evidence operations layer** that sits beside an existing ATS and turns resumes, interview notes, assessments, and job requirements into a traceable review packet.

The product promise should be narrower and more defensible than “avoid wrong hires”:

> **RecruitmentGuard helps hiring teams move from messy hiring evidence to a reviewable, source-cited packet without losing context, consent, or human control.**

AI can reduce repetitive cognitive work in recruiting, but published research also identifies concerns around cost, privacy, bias, and replacement of human judgment.[1] The product should therefore make the human reviewer more effective rather than silently replacing the reviewer.

## Market and buyer hypotheses

These are hypotheses to validate through customer interviews and workflow pilots, not established market facts.

| Segment | Acute pain | Likely willingness to adopt | Integration reality | Recommended priority |
|---|---|---|---|---|
| Scaling startup or scale-up hiring technical roles | Hiring managers and recruiters repeatedly reconcile resumes, transcripts, take-homes, and changing requirements with little operations support | High if setup takes minutes and the product works with existing documents and ATS exports | Often willing to start with CSV, JSON, email-forwarding, or shared-folder workflows | **Primary beachhead** |
| Small engineering team hiring intermittently | High reviewer context-switching and inconsistent notes, but low volume and low budget | Moderate; needs a lightweight no-admin workflow | Should work without an ATS integration | **Secondary beachhead** |
| Enterprise recruiting operations | Strong need for auditability, governance, consistency, and integration controls | High potential contract value, but long security and procurement cycles | Requires least-privilege APIs, retention controls, audit logs, SSO, and vendor review | **Later expansion** |
| Staffing or recruiting agencies | Repeated evidence assembly across clients and roles | Potentially high because workflow repetition is frequent | Needs multi-tenant separation and client-specific policies | **Discovery hypothesis** |

Greenhouse explicitly positions its APIs as a way to access and update candidate data and support different hiring workflows, including attachments and application movement.[2] This supports an integration strategy based on **adjacent workflow augmentation**, not ATS replacement. The first integration should be read-only and export-friendly; write-back should be opt-in and human-confirmed.

## Product-market-fit opportunities

### 1. Evidence QA for recruiter and hiring-manager handoffs

The immediate value is reducing the repeated work of locating the exact resume line, transcript answer, assessment date, and requirement that support a discussion. This is more measurable than promising better hiring outcomes. Core outputs should be a source-cited brief, unresolved questions, contradictions, stale evidence, and a compact handoff packet.

### 2. Job-description and hiring-profile normalization

Modern JDs mix must-have requirements, preferred skills, responsibilities, operating context, interview competencies, location constraints, and process language. RecruitmentGuard should convert those into a versioned requirement profile with explicit priority and evidence policy. It should preserve the original JD and show which requirement was derived from which span.

### 3. Review workflow orchestration

The product can save time by routing packets to the correct reviewer, recording resolution notes, requesting missing evidence, and preventing premature finalization. This is valuable across startup, enterprise, and small-team settings without changing the underlying evidence rule.

### 4. Evidence and process analytics

Analytics should answer operational questions: which requirements are routinely unsupported, where interviews create ambiguity, how many packets need manual review, how long review takes, and which workflows produce repeated rework. These metrics are safer and more actionable than predicting candidate quality.

### 5. Integration without a technical project

A non-technical team should be able to start with a folder upload or CSV/JSON export, choose a profile, review packets, and export Markdown/PDF/JSON results. The integration ladder should be:

| Level | Interface | Intended customer |
|---|---|---|
| 0 | Local or hosted web upload with CSV/JSON export | Small teams and pilots |
| 1 | Shared-folder and email-forwarding adapters | Teams without engineering support |
| 2 | Read-only ATS connector and scheduled sync | Scaling teams |
| 3 | Webhooks and human-confirmed write-back | Enterprise recruiting operations |

Greenhouse’s developer resources include APIs, webhooks, and integration documentation.[2] The product should use the same connector-neutral internal model for any ATS rather than coupling the core validator to one vendor.

## Sensitive feature boundaries

The requested areas are valuable only if represented as explicit, candidate-provided or job-defined workflow facts. They must not become hidden suitability scores.

| Requested area | Safe product form | Prohibited or unsafe form |
|---|---|---|
| Cultural fit | Work-practice alignment: collaboration cadence, decision style, documentation expectations, and meeting constraints explicitly stated by the role and discussed by the candidate | Personality inference, “culture fit” score, similarity-to-team ranking, or protected-trait proxy |
| Remote-only or hybrid fit | Mutual preference and logistics ledger: location, time-zone overlap, travel expectations, equipment, and candidate consent | Inferring commitment, productivity, family situation, health, or lifestyle from transcript language |
| Fake candidate signals | Consistency and provenance review: conflicting dates, unsupported claims, duplicate text, unverifiable references, or missing evidence, all shown as review questions | “Fraud probability,” deception detection, facial/voice analysis, or automated rejection |
| Sponsorship and visa | Candidate-provided work-authorization and sponsorship-needed fields with jurisdiction, date, consent, retention, and routing controls | Inferring nationality, ethnicity, immigration status, or using proxy signals to exclude a candidate |
| Consent | Versioned consent ledger: purpose, scope, timestamp, source, retention, withdrawal, and reviewer access | Treating silence as consent or reusing information outside the stated purpose |
| Cost of hire | Process analytics: time-to-review, recruiter touches, assessment cost, agency fee, rework, and time-to-fill | Candidate-level “cost risk,” salary-worthiness, or ranking by expected ROI |
| Core skills | Requirement-to-evidence coverage with exact spans, recency, depth context, and reviewer questions | Opaque skill score, automatic rejection, or ranking based on inferred potential |

NIST describes the AI Risk Management Framework as a way to improve the ability to incorporate trustworthiness into AI design, development, use, and evaluation.[3] RecruitmentGuard should turn that principle into product behavior: explicit scope, provenance, review checkpoints, measurable false positives, and auditable outputs.

The EEOC has specifically examined the use of AI and automated systems in employment and the risk that automated screening or matching can create discrimination concerns.[4] The product should therefore avoid presenting workflow evidence as a dispositive employment decision and should make the reviewer’s responsibility visible.

## Differentiation

The defensible distinction is not “our model is better at judging candidates.” It is:

1. **Evidence binding:** every material claim links to exact source text.
2. **Contradiction-first workflow:** conflicts and evidence gaps are surfaced before narrative synthesis.
3. **Hard human gate:** blocking findings prevent finalization until a reviewer resolves them.
4. **Profile-configured, not profile-biased:** startup, enterprise, and small-team profiles change requirements and questions, not the decision boundary.
5. **Integration-neutral:** the core model accepts documents and events from exports, folders, APIs, or webhooks.
6. **Operational analytics:** the product measures review workload and evidence quality rather than pretending to measure future employee performance.

## Next sprint: Evidence Operations Layer

### Sprint objective

Build a small, integration-neutral workflow layer that lets a non-technical recruiter configure a hiring profile, ingest a packet, see evidence and gaps, resolve a review item, and export a traceable brief and machine-readable audit record.

### Deliverables

| Workstream | Deliverable | Acceptance criterion |
|---|---|---|
| Canonical model | `schemas/v2_workflow_event.schema.json` and `schemas/consent_record.schema.json` | A packet can be represented independently of ATS vendor, with source, purpose, consent, retention, and event metadata |
| Requirement profile | Profile fields for work mode, time-zone overlap, travel, sponsorship workflow, core skills, and work-practice expectations | Every new field is a factual requirement or candidate-provided preference; no hidden score field exists |
| Import adapters | CSV/JSON/folder adapter with normalized packet events | A non-technical user can ingest a packet without API credentials or code |
| Review queue | Evidence issue queue with owner, status, due date, resolution note, and audit event | Blocking issues cannot be finalized; every resolution is attributable and timestamped |
| Brief export | Markdown and JSON export with citations and consent metadata | Export contains source spans, requirement coverage, unresolved questions, and no decision field |
| Analytics | Review time, issue count, rework count, missing-evidence rate, citation fidelity, and consent completeness | Metrics are computed from event logs and can be segmented by profile and role family |
| Tests | Unit, integration, and adversarial tests | V1 suite remains green; V2 suite covers consent withdrawal, missing source, contradictory work-mode requirements, and unsafe-field rejection |

### Evaluation design

The next benchmark should remain synthetic but become more operationally realistic. Add 24 packets: eight per profile, with clean, contradiction, missing-consent, stale-assessment, unsupported-claim, work-mode mismatch, sponsorship-routing, and hard-negative conditions. Keep ground truth separate from candidate-facing output.

| Metric | Definition | Target for next sprint |
|---|---|---:|
| Evidence citation fidelity | Cited span exactly matches source | ≥ 99% |
| Blocking-finding precision | Blocking findings that match planted blocking conditions | ≥ 95% |
| Blocking-finding recall | Planted blocking conditions surfaced | ≥ 90% |
| False blocking rate | Clean or hard-negative packets blocked | ≤ 5% |
| Review queue completeness | Every blocking issue has owner, status, and audit event | 100% |
| Consent completeness | Packets with explicit purpose, scope, timestamp, and retention | 100% |
| Integration setup effort | Steps from clean export to first brief | ≤ 5 documented steps |
| Reviewer workload | Median minutes or reviewer touches per packet | Measure first; do not set a quality claim yet |

### Deliberately out of scope

Do not build cultural-fit scoring, deception probability, visa or sponsorship eligibility judgment, automated candidate rejection, candidate-level cost scoring, facial or voice analysis, ATS write-back without confirmation, or any protected-trait inference. These are either unsafe, difficult to validate, or unnecessary for the evidence-operations wedge.

## Release discipline

Keep V1 frozen under `v1.0.0` and V2.0 frozen under `v2.0.0`. Build the next work as an additive `v2.1` milestone. Every meaningful change must add a changelog row with the evaluation evidence from the same run. Promote to a new release only after a clean-checkout reproduction, ground-rules check, metrics consistency check, and tag verification.

## References

[1]: https://pmc.ncbi.nlm.nih.gov/articles/PMC9516509/ "Collaboration among recruiters and artificial intelligence: removing human prejudices in employment"
[2]: https://www.greenhouse.com/api "Greenhouse APIs"
[3]: https://www.nist.gov/itl/ai-risk-management-framework "NIST AI Risk Management Framework"
[4]: https://www.eeoc.gov/meetings/meeting-january-31-2023-navigating-employment-discrimination-ai-and-automated-systems-new/transcript "EEOC meeting transcript on employment discrimination, AI, and automated systems"
