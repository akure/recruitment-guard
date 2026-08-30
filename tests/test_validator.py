from datetime import date, timedelta
import unittest

from validator.validate import Assessment, ExtractedFact, validate


class ValidatorTests(unittest.TestCase):
    def fact(self, fact_id, subject, claim, doc="cv"):
        return ExtractedFact(
            fact_id=fact_id,
            subject=subject,
            claim=claim,
            source_doc=doc,
            source_span=claim,
        )

    def test_conflicting_matching_subject_emits_one_contradiction(self):
        findings = validate(
            [self.fact("f1", "team_size_payments_migration", "led a team of 8 engineers")],
            [self.fact("t1", "team_size_payments_migration", "worked mostly solo", "transcript")],
            Assessment(score=84, date=date(2026, 8, 15)),
            as_of=date(2026, 8, 30),
            conflict_fn=lambda a, b: True,
        )
        self.assertEqual([f.type for f in findings], ["contradiction"])
        self.assertEqual(findings[0].subject, "team_size_payments_migration")
        self.assertEqual(findings[0].severity, "block")

    def test_consistent_matching_subject_is_not_flagged(self):
        findings = validate(
            [self.fact("f1", "ownership_payments_migration", "led the migration")],
            [self.fact("t1", "ownership_payments_migration", "I drove that project", "transcript")],
            Assessment(score=84, date=date(2026, 8, 15)),
            as_of=date(2026, 8, 30),
            conflict_fn=lambda a, b: False,
        )
        self.assertEqual(findings, [])

    def test_cv_only_subject_is_not_compared(self):
        findings = validate(
            [self.fact("f1", "skill_claim_go", "strong Go developer")],
            [],
            Assessment(score=84, date=date(2026, 8, 15)),
            as_of=date(2026, 8, 30),
            conflict_fn=lambda a, b: self.fail("conflict function should not be called"),
        )
        self.assertEqual(findings, [])

    def test_missing_assessment_emits_missing_evidence(self):
        findings = validate([], [], None, as_of=date(2026, 8, 30))
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].type, "missing_evidence")
        self.assertEqual(findings[0].severity, "block")

    def test_old_assessment_emits_stale_evidence(self):
        findings = validate(
            [], [], Assessment(score=75, date=date(2026, 8, 30) - timedelta(days=181)),
            as_of=date(2026, 8, 30),
        )
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].type, "stale_evidence")
        self.assertEqual(findings[0].subject, "assessment")

    def test_current_assessment_is_not_flagged(self):
        findings = validate(
            [], [], Assessment(score=75, date=date(2026, 8, 30) - timedelta(days=180)),
            as_of=date(2026, 8, 30),
        )
        self.assertEqual(findings, [])

    def test_multiple_subjects_are_isolated(self):
        findings = validate(
            [
                self.fact("f1", "team_size_payments_migration", "led a team of 8"),
                self.fact("f2", "ownership_ledger", "owned the ledger service"),
            ],
            [
                self.fact("t1", "team_size_payments_migration", "worked mostly solo", "transcript"),
                self.fact("t2", "ownership_ledger", "drove the ledger service", "transcript"),
            ],
            Assessment(score=82, date=date(2026, 8, 30)),
            as_of=date(2026, 8, 30),
            conflict_fn=lambda a, b: a == "led a team of 8",
        )
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].subject, "team_size_payments_migration")


if __name__ == "__main__":
    unittest.main()
