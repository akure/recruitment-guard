import csv
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from workflow.importer import import_source
from workflow.run import run


ROOT = Path(__file__).resolve().parents[1]
PACKETS = ROOT / "data_ops"


class WorkflowRunTests(unittest.TestCase):
    def test_folder_import_emits_normalized_packet_event(self):
        records = import_source(PACKETS / "packet_001")
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["ingestion_source"], "folder")
        self.assertEqual(records[0]["events"][0]["event_type"], "packet_ingested")
        self.assertEqual(records[0]["events"][0]["payload"]["source"], "folder")

    def test_csv_and_json_manifests_resolve_relative_packet_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            csv_path = root / "packets.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["packet_path"])
                writer.writeheader()
                writer.writerow({"packet_path": str(PACKETS / "packet_001")})
            json_path = root / "packets.json"
            json_path.write_text(json.dumps({"packets": [{"packet_path": str(PACKETS / "packet_002")}]}) + "\n", encoding="utf-8")
            self.assertEqual(import_source(csv_path)[0]["packet_id"], "001")
            self.assertEqual(import_source(json_path)[0]["packet_id"], "002")

    def test_run_exports_brief_and_audit_for_clean_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            summary = run(PACKETS / "packet_001", output, date(2026, 8, 30), "recruiter")
            self.assertEqual(summary["states"]["finalized"], 1)
            self.assertTrue((output / "packet_001" / "brief.md").exists())
            audit = json.loads((output / "packet_001" / "audit.json").read_text())
            self.assertEqual(audit["consent_id"], "consent-001")
            self.assertTrue(any(event["event_type"] == "brief_exported" for event in audit["events"]))
            brief = (output / "packet_001" / "brief.md").read_text()
            self.assertIn("contains no hire/no-hire recommendation or score", brief.lower())

    def test_run_exports_blocking_review_queue_without_brief(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "out"
            summary = run(PACKETS / "packet_003", output, date(2026, 8, 30), "recruiter")
            self.assertEqual(summary["states"]["pending_review"], 1)
            audit_path = output / "packet_003" / "audit.json"
            audit = json.loads(audit_path.read_text())
            self.assertGreaterEqual(len(audit["review_items"]), 1)
            item = audit["review_items"][0]
            self.assertEqual(item["owner"], "recruiter")
            self.assertEqual(item["status"], "open")
            self.assertFalse((output / "packet_003" / "brief.md").exists())


if __name__ == "__main__":
    unittest.main()
