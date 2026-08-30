import json
import unittest
from pathlib import Path

from analytics.metrics import aggregate_metrics, render_metrics
from ops.events import make_event


class OperationsAnalyticsTests(unittest.TestCase):
    def test_aggregates_review_time_and_rework_from_events(self):
        events = [
            make_event("001", "packet_ingested", "system", {}, "2026-08-30T10:00:00Z"),
            make_event("001", "review_requested", "system", {"finding_count": 2}, "2026-08-30T10:02:00Z"),
            make_event("001", "finding_resolved", "recruiter", {"review_id": "r1"}, "2026-08-30T10:12:00Z"),
            make_event("001", "brief_exported", "recruiter", {"rework_count": 1}, "2026-08-30T10:15:00Z"),
        ]
        row = aggregate_metrics([{"packet_id": "001", "profile_id": "startup", "consent_status": "granted", "events": events}])["metrics"]
        self.assertEqual(row["packets_requiring_review"], 1)
        self.assertEqual(row["median_review_minutes"], 10.0)
        self.assertEqual(row["rework_events"], 1)
        self.assertEqual(row["consent_completeness_rate"], 1.0)

    def test_profile_rows_and_safety_boundary_are_rendered(self):
        records = [
            {"packet_id": "001", "profile_id": "startup", "consent_status": "granted", "events": []},
            {"packet_id": "009", "profile_id": "enterprise", "consent_status": "withdrawn", "events": []},
        ]
        result = aggregate_metrics(records)
        report = render_metrics(result)
        self.assertIn("startup", report)
        self.assertIn("enterprise", report)
        self.assertIn("consent completeness", report.lower())
        self.assertIn("Operational workflow metrics only", report)
        self.assertNotIn("candidate_score", report)
        self.assertNotIn("hireability", report.lower())

    def test_24_packet_fixture_is_available_for_metrics_runner(self):
        manifest = json.loads(Path("data_ops/MANIFEST.json").read_text())
        self.assertEqual(manifest["packet_count"], 24)
        self.assertEqual(len({p["profile_id"] for p in manifest["packets"]}), 3)


if __name__ == "__main__":
    unittest.main()
