import json
import tempfile
import unittest
from pathlib import Path

from ops.consent import validate_consent
from ops.ingest import ingest_packet
from ops.events import make_event
from ops.review import create_review_item, resolve_review_item


class EvidenceOperationsTests(unittest.TestCase):
    def test_ingest_normalizes_packet_without_vendor_dependency(self):
        packet = Path("data_ops/packet_001")
        normalized = ingest_packet(packet)
        self.assertEqual(normalized["packet_id"], "001")
        self.assertEqual(normalized["profile_id"], "startup")
        self.assertEqual(normalized["source_files"], ["assessment.json", "consent.json", "cv.md", "jd.md", "profile.json", "transcript.md"])
        self.assertEqual(normalized["ingestion_source"], "folder")

    def test_consent_must_have_purpose_scope_and_retention(self):
        consent = json.loads(Path("data_ops/packet_001/consent.json").read_text())
        self.assertTrue(validate_consent(consent))
        invalid = dict(consent)
        invalid["scope"] = []
        with self.assertRaises(ValueError):
            validate_consent(invalid)

    def test_withdrawn_consent_is_not_treated_as_active(self):
        consent = json.loads(Path("data_ops/packet_003/consent.json").read_text())
        consent["status"] = "withdrawn"
        consent["withdrawn_at"] = "2026-08-30T10:00:00Z"
        self.assertFalse(validate_consent(consent, require_active=True))

    def test_workflow_event_is_attributable_and_typed(self):
        event = make_event("001", "review_requested", "system", {"finding_count": 2})
        self.assertTrue(event["event_id"])
        self.assertEqual(event["packet_id"], "001")
        self.assertEqual(event["event_type"], "review_requested")
        self.assertEqual(event["actor_type"], "system")
        self.assertEqual(event["payload"]["finding_count"], 2)

    def test_review_item_requires_owner_and_resolution_is_attributable(self):
        item = create_review_item("001", "conflicting_evidence", ["e1", "e2"], owner="recruiter")
        self.assertEqual(item["status"], "open")
        resolved = resolve_review_item(item, "Recruiter confirmed the source context.", actor="recruiter")
        self.assertEqual(resolved["status"], "resolved")
        self.assertEqual(resolved["resolution"]["actor"], "recruiter")

    def test_benchmark_manifest_has_expected_contexts_and_conditions(self):
        manifest = json.loads(Path("data_ops/MANIFEST.json").read_text())
        self.assertEqual(manifest["packet_count"], 24)
        self.assertEqual({p["profile_id"] for p in manifest["packets"]}, {"startup", "enterprise", "small_team"})
        self.assertEqual({p["condition"] for p in manifest["packets"]}, {"clean", "contradiction", "missing_consent", "stale_assessment", "unsupported_claim", "work_mode_mismatch", "sponsorship_routing", "hard_negative"})
        self.assertTrue(all(p["synthetic_only"] for p in manifest["packets"]))


if __name__ == "__main__":
    unittest.main()
