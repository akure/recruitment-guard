import unittest
from datetime import date
from pathlib import Path

from extraction.v2_extract import extract_packet
from validator.v2_validate import validate_v2
from checkpoint.v2_brief import render_v2_brief


class V2ValidationBriefTests(unittest.TestCase):
    def bundle(self, packet_id):
        packet = Path("data_v2") / f"packet_{packet_id:03d}"
        bundle = extract_packet(packet, mock=True)
        assessment = None
        if (packet / "assessment.json").exists():
            import json
            assessment = json.loads((packet / "assessment.json").read_text())
        return packet, bundle, assessment

    def test_clean_packet_has_profile_coverage_and_no_blocking_findings(self):
        packet, bundle, assessment = self.bundle(2)
        result = validate_v2(bundle, assessment=assessment, as_of=date(2026, 8, 30))
        self.assertTrue(result["coverage"])
        self.assertIn("supported", {item["status"] for item in result["coverage"]})
        self.assertFalse([f for f in result["findings"] if f["severity"] == "block"])

    def test_contradictory_scope_is_deterministically_blocking(self):
        packet, bundle, assessment = self.bundle(1)
        result = validate_v2(bundle, assessment=assessment, as_of=date(2026, 8, 30))
        types = {f["type"] for f in result["findings"]}
        self.assertIn("conflicting_evidence", types)
        self.assertTrue(any(f["severity"] == "block" for f in result["findings"]))

    def test_stale_assessment_is_blocking(self):
        packet, bundle, assessment = self.bundle(6)
        result = validate_v2(bundle, assessment=assessment, as_of=date(2026, 8, 30))
        self.assertIn("stale_evidence", {f["type"] for f in result["findings"]})
        self.assertTrue(any(f["severity"] == "block" for f in result["findings"]))

    def test_ambiguous_and_uncorroborated_are_visible_without_false_direct_label(self):
        packet, bundle, assessment = self.bundle(4)
        result = validate_v2(bundle, assessment=assessment, as_of=date(2026, 8, 30))
        self.assertIn("ambiguous_evidence", {f["type"] for f in result["findings"]})
        self.assertIn("uncorroborated_evidence", {f["type"] for f in result["findings"]})

    def test_brief_has_profile_sections_and_no_decision_language(self):
        packet, bundle, assessment = self.bundle(4)
        result = validate_v2(bundle, assessment=assessment, as_of=date(2026, 8, 30))
        brief = render_v2_brief(bundle, result)
        for heading in ("Supported evidence", "Conflicting evidence", "Stale evidence", "Ambiguous evidence", "Uncorroborated evidence", "Questions for reviewer"):
            self.assertIn(heading, brief)
        self.assertIn("This brief presents evidence only", brief)
        self.assertNotIn("decision:", brief.lower())
        self.assertNotIn("score:", brief.lower())


if __name__ == "__main__":
    unittest.main()
