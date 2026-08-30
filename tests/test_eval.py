import tempfile
import unittest
from pathlib import Path

from eval.harness import evaluate_records, render_metrics


class EvaluationTests(unittest.TestCase):
    def test_scores_three_planted_cases_and_nine_clean_controls(self):
        records = [
            {"packet_id": "01", "baseline_surface": False, "guarded_findings": [{"type": "contradiction"}]},
            {"packet_id": "02", "baseline_surface": False, "guarded_findings": [{"type": "contradiction"}]},
            {"packet_id": "03", "baseline_surface": False, "guarded_findings": [{"type": "missing_evidence"}]},
        ] + [
            {"packet_id": f"{i:02d}", "baseline_surface": False, "guarded_findings": []}
            for i in range(4, 13)
        ]
        summary = evaluate_records(records)
        self.assertEqual(summary["baseline_planted_surfaced"], 0)
        self.assertEqual(summary["guarded_planted_surfaced"], 3)
        self.assertEqual(summary["guarded_false_positives"], 0)

    def test_metrics_uses_required_table_shape_and_measured_values(self):
        summary = {
            "baseline_planted_surfaced": 0,
            "guarded_planted_surfaced": 3,
            "guarded_false_positives": 0,
            "baseline_avg_time_seconds": 0.01,
            "guarded_avg_time_seconds": 0.02,
            "baseline_avg_tokens": 100,
            "guarded_avg_tokens": 200,
        }
        text = render_metrics(summary)
        self.assertIn("| Planted cases surfaced (of 3)    | 0 | 3 | +3 |", text)
        self.assertIn("| False positives (of 9 clean)     | n/a | 0 | — |", text)
        self.assertIn("| Avg. token cost per packet       | 100 | 200 | +100 |", text)


if __name__ == "__main__":
    unittest.main()
