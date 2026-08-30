from datetime import date
import json
import tempfile
import unittest
from pathlib import Path

from checkpoint.workflow import (
    Assessment,
    ExtractedFact,
    create_pending_review,
    finalize_packet,
    render_brief,
    resolve_finding,
)
from validator.validate import ValidatorFinding


class CheckpointTests(unittest.TestCase):
    def fact(self, fact_id, doc, subject, claim):
        return ExtractedFact(fact_id, subject, claim, doc, claim)

    def finding(self, finding_id="c1", subject="team_size_payments_migration"):
        return ValidatorFinding(
            finding_id=finding_id,
            type="contradiction",
            subject=subject,
            sources=[
                {"doc": "cv", "fact_id": "f1", "span": "led a team of 8 engineers"},
                {"doc": "transcript", "fact_id": "t1", "span": "worked mostly solo"},
            ],
        )

    def test_unresolved_blocking_finding_cannot_finalize(self):
        with tempfile.TemporaryDirectory() as tmp:
            pending = Path(tmp) / "pending.json"
            brief = Path(tmp) / "brief.md"
            create_pending_review("01", [self.finding()], pending)
            with self.assertRaises(PermissionError):
                finalize_packet("01", pending, brief, [], [], None)
            self.assertFalse(brief.exists())

    def test_resolution_allows_finalization_and_is_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            pending = Path(tmp) / "pending.json"
            brief = Path(tmp) / "brief.md"
            create_pending_review("01", [self.finding()], pending)
            resolve_finding(pending, "c1", "Recruiter confirmed scope was split across two workstreams.")
            output = finalize_packet(
                "01", pending, brief,
                [self.fact("f1", "cv", "team_size_payments_migration", "led a team of 8 engineers")],
                [self.fact("t1", "transcript", "team_size_payments_migration", "worked mostly solo")],
                Assessment(84, date(2026, 8, 15)),
            )
            text = output.read_text()
            self.assertIn("Recruiter confirmed scope", text)
            self.assertIn("Source: CV", text)
            self.assertIn("Source: Transcript", text)
            self.assertIn("contains no hire/no-hire recommendation or score", text)
            saved = json.loads(pending.read_text())
            self.assertEqual(saved["findings"][0]["resolution"], "Recruiter confirmed scope was split across two workstreams.")

    def test_clean_packet_finalizes_without_checkpoint(self):
        text = render_brief("04", [], [], None, [])
        self.assertIn("## Candidate Evidence Brief — Packet 04 — Backend Engineer (Series B fintech)", text)
        self.assertIn("This brief presents evidence only", text)
        self.assertIn("contains no hire/no-hire recommendation or score", text)
        self.assertNotIn("### ⚠ Flagged for review", text)

    def test_resolve_rejects_unknown_finding(self):
        with tempfile.TemporaryDirectory() as tmp:
            pending = Path(tmp) / "pending.json"
            create_pending_review("01", [self.finding()], pending)
            with self.assertRaises(KeyError):
                resolve_finding(pending, "unknown", "note")


if __name__ == "__main__":
    unittest.main()
