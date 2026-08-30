import json
import tempfile
import unittest
from pathlib import Path

from extraction.v2_extract import extract_packet, validate_bundle


class V2ExtractionTests(unittest.TestCase):
    def test_profile_aware_bundle_contains_requirements_and_questions(self):
        bundle = extract_packet(Path("data_v2/packet_001"), mock=True)
        self.assertEqual(bundle["schema_version"], "v2.1")
        self.assertEqual(bundle["profile_id"], "startup")
        self.assertEqual(bundle["role_family"], "backend_platform")
        self.assertGreaterEqual(len(bundle["requirements"]), 6)
        self.assertGreaterEqual(len(bundle["review_questions"]), 2)
        self.assertTrue({r["priority"] for r in bundle["requirements"]} >= {"must_have", "preferred"})

    def test_evidence_has_richer_provenance_and_exact_source_span(self):
        packet = Path("data_v2/packet_001")
        bundle = extract_packet(packet, mock=True)
        self.assertGreaterEqual(len(bundle["evidence"]), 5)
        for evidence in bundle["evidence"]:
            source = (packet / f"{evidence['source']['source_doc']}.md").read_text()
            span = evidence["source"]["source_span"]
            start, end = evidence["source"]["span_offset"]
            self.assertEqual(source[start:end], span)
            self.assertIn(evidence["evidence_quality"], {"direct", "specific", "ambiguous", "uncorroborated", "uncertain"})
            self.assertGreaterEqual(evidence["confidence"], 0)
            self.assertLessEqual(evidence["confidence"], 1)

    def test_ambiguous_scope_is_not_mislabeled_as_direct(self):
        bundle = extract_packet(Path("data_v2/packet_004"), mock=True)
        qualities = {e["evidence_quality"] for e in bundle["evidence"]}
        self.assertIn("ambiguous", qualities)

    def test_validate_bundle_rejects_bad_span(self):
        bundle = extract_packet(Path("data_v2/packet_001"), mock=True)
        bundle["evidence"][0]["source"]["span_offset"][0] += 1
        with self.assertRaises(ValueError):
            validate_bundle(bundle, Path("data_v2/packet_001"))

    def test_all_v2_packets_extract_in_mock_mode(self):
        packets = sorted(Path("data_v2").glob("packet_*"))
        self.assertEqual(len(packets), 12)
        for packet in packets:
            bundle = extract_packet(packet, mock=True)
            self.assertEqual(bundle["packet_id"], packet.name.rsplit("_", 1)[-1])
            self.assertTrue(bundle["evidence"])


if __name__ == "__main__":
    unittest.main()
