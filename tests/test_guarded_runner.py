from datetime import date
import json
import tempfile
import unittest
from pathlib import Path

from guarded.runner import run_packet, resume_packet
from checkpoint.workflow import resolve_finding


class GuardedRunnerTests(unittest.TestCase):
    def test_clean_packet_finalizes_and_logs_trajectory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = run_packet(
                "04", data_root=Path("data"), extraction_root=root / "extraction",
                pending_root=root / "pending", brief_root=root / "briefs",
                trajectory_root=root / "trajectories", mock=True,
                as_of=date(2026, 8, 30),
            )
            self.assertEqual(result["state"], "finalized")
            self.assertTrue((root / "briefs/brief_guarded_04.md").exists())
            trajectory = json.loads((root / "trajectories/packet_04.json").read_text())
            self.assertIn("stage_1_extraction", trajectory)
            self.assertEqual(trajectory["stage_2_validation"], [])
            self.assertEqual(trajectory["stage_3_pause"]["paused"], False)
            self.assertTrue(trajectory["stage_4_final_brief"].endswith("brief_guarded_04.md"))

    def test_missing_assessment_pauses_and_resume_requires_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = run_packet(
                "03", data_root=Path("data"), extraction_root=root / "extraction",
                pending_root=root / "pending", brief_root=root / "briefs",
                trajectory_root=root / "trajectories", mock=True,
                as_of=date(2026, 8, 30),
            )
            self.assertEqual(result["state"], "pending_review")
            self.assertFalse((root / "briefs/brief_guarded_03.md").exists())
            pending = root / "pending/packet_03.json"
            payload = json.loads(pending.read_text())
            self.assertEqual(payload["findings"][0]["type"], "missing_evidence")
            finding_id = payload["findings"][0]["finding_id"]
            with self.assertRaises(PermissionError):
                resume_packet("03", pending, root / "extraction", Path("data"), root / "briefs", root / "trajectories")
            resolve_finding(pending, finding_id, "Recruiter acknowledged that no assessment was on file.")
            final = resume_packet("03", pending, root / "extraction", Path("data"), root / "briefs", root / "trajectories")
            self.assertEqual(final["state"], "finalized")
            text = (root / "briefs/brief_guarded_03.md").read_text()
            self.assertIn("Recruiter acknowledged", text)
            trajectory = json.loads((root / "trajectories/packet_03.json").read_text())
            self.assertEqual(trajectory["stage_3_pause"]["paused"], True)
            self.assertEqual(trajectory["stage_3_pause"]["resolved_by"], "recruiter")
            self.assertTrue(trajectory["stage_4_final_brief"].endswith("brief_guarded_03.md"))


if __name__ == "__main__":
    unittest.main()
