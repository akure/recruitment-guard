import unittest

from eval.v2_harness import evaluate_v2_records, render_v2_metrics


class V2EvaluationTests(unittest.TestCase):
    def test_scores_contexts_and_finding_recall(self):
        records = [
            {"packet_id": "001", "profile_id": "startup", "condition": "contradiction", "findings": [{"type": "conflicting_evidence", "severity": "block"}], "state": "pending_review", "citation_fidelity": 1.0, "review_questions": 2},
            {"packet_id": "002", "profile_id": "enterprise", "condition": "clean", "findings": [], "state": "finalized", "citation_fidelity": 1.0, "review_questions": 2},
            {"packet_id": "003", "profile_id": "small_team", "condition": "missing_assessment", "findings": [{"type": "missing_evidence", "severity": "block"}], "state": "pending_review", "citation_fidelity": 1.0, "review_questions": 2},
        ]
        summary = evaluate_v2_records(records)
        self.assertEqual(summary["context_counts"], {"startup": 1, "enterprise": 1, "small_team": 1})
        self.assertEqual(summary["expected_findings_surfaced"], 2)
        self.assertEqual(summary["expected_findings_total"], 2)
        self.assertEqual(summary["finding_recall"], 1.0)
        self.assertEqual(summary["blocking_false_positives"], 0)
        self.assertEqual(summary["citation_fidelity"], 1.0)

    def test_reviewer_burden_is_measured_from_records(self):
        records = [
            {"packet_id": "001", "profile_id": "startup", "condition": "contradiction", "findings": [{"type": "conflicting_evidence", "severity": "block"}], "state": "pending_review", "citation_fidelity": 1.0, "review_questions": 2},
            {"packet_id": "002", "profile_id": "enterprise", "condition": "clean", "findings": [], "state": "finalized", "citation_fidelity": 1.0, "review_questions": 3},
        ]
        summary = evaluate_v2_records(records)
        burden = summary["reviewer_burden"]
        self.assertEqual(burden["packets_requiring_review"], 1)
        self.assertEqual(burden["review_rate"], 0.5)
        self.assertEqual(burden["blocking_findings"], 1)
        self.assertEqual(burden["avg_review_questions_per_packet"], 2.5)
        self.assertEqual(burden["avg_blocking_findings_per_review_packet"], 1.0)

    def test_metrics_has_profile_rows_and_safety_boundary(self):
        metrics = render_v2_metrics({
            "context_counts": {"enterprise": 1, "small_team": 1, "startup": 1},
            "expected_findings_surfaced": 2,
            "expected_findings_total": 3,
            "finding_recall": 0.6667,
            "blocking_false_positives": 1,
            "citation_fidelity": 0.95,
            "reviewer_burden": {"packets_requiring_review": 2, "review_rate": 0.6667, "blocking_findings": 2, "avg_review_questions_per_packet": 2.0, "avg_blocking_findings_per_review_packet": 1.0},
            "per_profile": {
                "startup": {"packets": 1, "expected_findings_surfaced": 1, "expected_findings_total": 1, "finding_recall": 1.0, "review_packets": 1, "review_rate": 1.0, "citation_fidelity": 1.0},
                "enterprise": {"packets": 1, "expected_findings_surfaced": 1, "expected_findings_total": 1, "finding_recall": 1.0, "review_packets": 0, "review_rate": 0.0, "citation_fidelity": 1.0},
                "small_team": {"packets": 1, "expected_findings_surfaced": 0, "expected_findings_total": 1, "finding_recall": 0.0, "review_packets": 1, "review_rate": 1.0, "citation_fidelity": 0.85},
            },
        })
        self.assertIn("startup", metrics)
        self.assertIn("Finding recall", metrics)
        self.assertIn("Reviewer burden", metrics)
        self.assertIn("evidence only", metrics.lower())
        self.assertNotIn("candidate score:", metrics.lower())
        self.assertNotIn("ranking:", metrics.lower())
        self.assertNotIn("decision:", metrics.lower())


if __name__ == "__main__":
    unittest.main()
