import sys, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from keyu_harness.scenario import load_scenario, run_scenario
from keyu_harness.ledger import (
    validate_csv, validate_claim_source_links, validate_artifact_source_links, SOURCE_FIELDS, CLAIM_FIELDS, ARTIFACT_FIELDS
)

class SimulatorTests(unittest.TestCase):
    def test_t5_mismatch_is_flagged_as_synthetic(self):
        report, events, inputs = run_scenario(ROOT / "scenarios/t5_metadata_mismatch.json")
        self.assertEqual(report["data_class"], "SIMULATED")
        self.assertGreaterEqual(len(report["findings"]), 1)
        self.assertTrue(all(e["source_kind"] == "synthetic_fixture" for e in events))

    def test_trace_outliers_are_flagged(self):
        report, events, inputs = run_scenario(ROOT / "scenarios/distributed_trace_anomaly.json")
        self.assertEqual(report["data_class"], "SIMULATED")
        self.assertGreaterEqual(len(report["findings"]), 1)
        self.assertTrue(any(e.get("flagged") for e in events))

    def test_unmarked_scenario_is_rejected(self):
        import tempfile, json
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bad.json"
            p.write_text(json.dumps({"scenario_id":"x","kind":"trace_anomaly","notice":"real"}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_scenario(p)

    def test_source_registry_validates(self):
        self.assertEqual(validate_csv(ROOT / "references" / "source_registry.csv", SOURCE_FIELDS), [])

    def test_claim_ledger_validates(self):
        self.assertEqual(validate_csv(ROOT / "references" / "claim_ledger.csv", CLAIM_FIELDS), [])


    def test_artifact_registry_validates(self):
        self.assertEqual(validate_csv(ROOT / "references" / "artifact_registry.csv", ARTIFACT_FIELDS), [])

    def test_artifact_source_ids_resolve(self):
        self.assertEqual(
            validate_artifact_source_links(
                ROOT / "references" / "artifact_registry.csv",
                ROOT / "references" / "source_registry.csv"
            ), []
        )

    def test_claim_source_ids_resolve(self):
        self.assertEqual(
            validate_claim_source_links(
                ROOT / "references" / "claim_ledger.csv",
                ROOT / "references" / "source_registry.csv"
            ), []
        )

if __name__ == "__main__":
    unittest.main()
