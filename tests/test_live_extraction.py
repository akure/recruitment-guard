import unittest

from extraction.extract import _validate


class LiveExtractionSafetyTests(unittest.TestCase):
    def test_unique_span_offset_is_repaired_deterministically(self):
        source = "- Led payments migration\n"
        data = {
            "source_doc": "cv",
            "packet_id": "01",
            "facts": [{
                "fact_id": "c1",
                "subject": "ownership_payments_migration",
                "claim": "Led payments migration",
                "source_span": "Led payments migration",
                "span_offset": [0, 3],
            }],
        }
        repaired = _validate(data, source, "cv", "01")
        self.assertEqual(repaired["facts"][0]["span_offset"], [2, 24])

    def test_duplicate_span_fails_closed(self):
        source = "- Led payments migration\n- Led payments migration\n"
        data = {
            "source_doc": "cv",
            "packet_id": "01",
            "facts": [{
                "fact_id": "c1",
                "subject": "ownership_payments_migration",
                "claim": "Led payments migration",
                "source_span": "Led payments migration",
                "span_offset": [2, 24],
            }],
        }
        with self.assertRaises(ValueError):
            _validate(data, source, "cv", "01")


if __name__ == "__main__":
    unittest.main()
