from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
import re
from typing import Callable, Iterable

STALENESS_THRESHOLD_DAYS = 180
ConflictFn = Callable[[str, str], bool]


@dataclass(frozen=True)
class ExtractedFact:
    fact_id: str
    subject: str
    claim: str
    source_doc: str
    source_span: str

    def as_source(self) -> dict[str, str]:
        return {"doc": self.source_doc, "fact_id": self.fact_id, "span": self.source_span}


@dataclass(frozen=True)
class Assessment:
    score: int | float
    date: date


@dataclass
class ValidatorFinding:
    finding_id: str
    type: str
    subject: str
    sources: list[dict[str, str]] = field(default_factory=list)
    severity: str = "block"
    resolution: str | None = None

    def as_dict(self) -> dict:
        return {
            "finding_id": self.finding_id,
            "type": self.type,
            "subject": self.subject,
            "sources": self.sources,
            "severity": self.severity,
            "resolution": self.resolution,
        }


def _parse_date(value: date | str) -> date:
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()


def _default_conflict(a: str, b: str) -> bool:
    """Conservative local fallback; production may inject the narrow model classifier."""
    left, right = f" {a.lower()} ", f" {b.lower()} "
    left_solo = any(token in left for token in (" solo ", " mostly me ", " worked alone "))
    right_solo = any(token in right for token in (" solo ", " mostly me ", " worked alone "))
    team_left = re.search(r"team of\s+(\d+)", left)
    team_right = re.search(r"team of\s+(\d+)", right)
    leadership_claim = any(token in left or token in right for token in (" led ", " owning ", " drove ", " owned "))
    if left_solo != right_solo and (team_left or team_right or leadership_claim):
        return True
    expert_left = " expert " in left
    expert_right = " expert " in right
    vague_left = any(token in left for token in (" didn't really", "did not really", "not really", "vague"))
    vague_right = any(token in right for token in (" didn't really", "did not really", "not really", "vague"))
    return (expert_left and vague_right) or (expert_right and vague_left)


def validate(
    cv_facts: Iterable[ExtractedFact],
    transcript_facts: Iterable[ExtractedFact],
    assessment: Assessment | None,
    *,
    as_of: date | None = None,
    staleness_threshold_days: int = STALENESS_THRESHOLD_DAYS,
    conflict_fn: ConflictFn | None = None,
) -> list[ValidatorFinding]:
    """Return blocking findings; the control flow deciding block/no-block is deterministic."""
    cv_by_subject = {fact.subject: fact for fact in cv_facts}
    tx_by_subject = {fact.subject: fact for fact in transcript_facts}
    classifier = conflict_fn or _default_conflict
    findings: list[ValidatorFinding] = []
    next_id = 1

    for subject in sorted(cv_by_subject.keys() & tx_by_subject.keys()):
        cv_fact = cv_by_subject[subject]
        tx_fact = tx_by_subject[subject]
        if classifier(cv_fact.claim, tx_fact.claim):
            findings.append(ValidatorFinding(
                finding_id=f"c{next_id}",
                type="contradiction",
                subject=subject,
                sources=[cv_fact.as_source(), tx_fact.as_source()],
            ))
            next_id += 1

    if assessment is None:
        findings.append(ValidatorFinding(
            finding_id=f"c{next_id}", type="missing_evidence", subject="assessment"
        ))
    else:
        reference_date = as_of or date.today()
        age_days = (reference_date - _parse_date(assessment.date)).days
        if age_days > staleness_threshold_days:
            findings.append(ValidatorFinding(
                finding_id=f"c{next_id}", type="stale_evidence", subject="assessment",
                sources=[{"doc": "assessment", "fact_id": "assessment", "span": str(assessment.date)}],
            ))
    return findings
