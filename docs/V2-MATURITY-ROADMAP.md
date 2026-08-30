# RecruitmentGuard V2 maturity roadmap

**Status:** Approved for sequential implementation after the frozen `v1.0.0` release.

## Product boundary

RecruitmentGuard V2 will use **realistic but entirely fictional** resumes, interview transcripts, assessments, and job descriptions. It will reproduce the complexity of modern hiring without importing real candidate data, identifiable public profiles, or private information.

The system remains an **evidence organization and review assistant**. It may surface evidence, uncertainty, contradictions, missing context, stale information, and reviewer questions. It must not rank candidates, assign hireability scores, infer protected traits, or issue hire/no-hire recommendations.

V1 remains frozen and reproducible. V2 work will use a separate `data_v2/` benchmark and additive, profile-aware modules rather than mutating the V1 benchmark semantics.

## Maturity tracks

| Track | V1 limitation | V2 direction |
|---|---|---|
| Hiring context | One Backend Engineer role and one company type | Profile-aware requirements for startup, enterprise, and small-team hiring |
| Job descriptions | Compact, clean, single-layer requirements | Realistic JDs with must-have versus preferred requirements, ownership scope, seniority signals, operating constraints, interview competencies, and context-specific trade-offs |
| Resumes | Short, highly structured bullets | Fictional modern resumes with career transitions, overlapping dates, consulting, promotions, impact claims, missing metrics, varied formatting, stack drift, and compressed project descriptions |
| Transcripts | Direct question-and-answer exchanges | Multi-stage interviews with follow-ups, hedging, corrections, interruptions, ambiguity, conflicting recollections, and uneven evidence quality |
| Evidence model | Claim/source-span pairs | Claim provenance, evidence quality, recency, corroboration, ambiguity, and unresolved reviewer questions |
| Validation | Contradiction and assessment freshness | Contradiction classes, timeline inconsistencies, scope inflation, unsupported superlatives, stale skills, requirement coverage gaps, and insufficient-evidence findings |
| Adaptability | Fixed logic for one role | Versioned hiring profiles that configure requirements and evidence policies without changing the safety boundary |
| Evaluation | Three planted cases plus clean controls | Cross-context benchmark with hard negatives, realistic ambiguity, citation fidelity, reviewer usefulness, and false-positive checks |

## Hiring profiles

The profiles configure what evidence is requested and how gaps are described. They do not create candidate scores or automatic decisions.

| Profile | Typical hiring reality | Evidence emphasis |
|---|---|---|
| **Startup** | Broad ownership, ambiguity tolerance, fast iteration, limited specialization | End-to-end ownership, adaptability, operating judgment, and delivery with incomplete structure |
| **Enterprise** | Larger systems, defined interfaces, compliance/process constraints, and cross-team collaboration | Scale, reliability, change management, cross-functional execution, role clarity, and sustained depth |
| **Small team** | Few engineers, high individual contribution, direct communication, and limited redundancy | Hands-on contribution, breadth, independent delivery, communication, and practical trade-offs |

## Sequential implementation milestones

### Milestone 1 — V2 scope and compatibility contract

Freeze V1 behavior. Add versioned profile/configuration schemas. Preserve V1 packet and brief compatibility, and define which new fields are optional versus required.

### Milestone 2 — Realistic synthetic dataset

Create `data_v2/` in one deterministic generation pass. Start with three profiles and at least four role families: backend/platform, product engineering, data/ML infrastructure, and security/reliability. Each packet contains `jd.md`, `cv.md`, `transcript.md`, optional `assessment.json`, and separate ground-truth annotations.

The benchmark should include clean cases, contradictions, missing evidence, stale evidence, ambiguous evidence, timeline inconsistencies, and hard negatives. Realism comes from language, chronology, specificity, interview behavior, and evidence quality—not from real people.

### Milestone 3 — Profile-aware extraction and provenance

Extract requirements, accomplishments, timelines, scope, technologies, and transcript evidence into typed structures. Add provenance, evidence quality, recency, corroboration, ambiguity, and reviewer-question fields while retaining exact source spans.

### Milestone 4 — Validation and profile-aware briefs

Extend deterministic checks for timeline overlap, requirement evidence gaps, claim strength versus support, stale evidence, and contradictory scope. Generate briefs with supported, conflicting, uncorroborated, stale, and questions-for-review sections.

### Milestone 5 — Cross-context evaluation and release

Evaluate across startup, enterprise, and small-team contexts. Measure contradiction recall, false-positive rate, citation fidelity, reviewer burden, and reproducibility. Tag mature milestones as `v2.0.0-alpha`, `v2.0.0-beta`, and `v2.0.0` only after cross-context verification.

## Engineering rule

Build **one configurable evidence pipeline** with profile files defining requirements and evidence policies. Do not create three duplicated systems. Every meaningful behavior change must update `CHANGELOG.md` in the same change set and include a relevant verification run.
