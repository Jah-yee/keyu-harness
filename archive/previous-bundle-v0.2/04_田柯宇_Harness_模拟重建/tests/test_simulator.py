import json, tempfile, unittest
from pathlib import Path
from thal.scenario import load_scenario, run_scenario

ROOT = Path(__file__).resolve().parents[1]

class SimulatorTests(unittest.TestCase):
    def test_t5_mismatch_is_flagged_as_synthetic(self):
        report, events, inputs = run_scenario(ROOT / "scenarios/t5_metadata_mismatch.json")
        self.assertEqual(report["evidence_grade"], "SIMULATED")
        self.assertGreaterEqual(len(report["findings"]), 1)
        self.assertTrue(all(e["source_kind"] == "synthetic_fixture" for e in events))

    def test_trace_outliers_are_flagged(self):
        report, events, inputs = run_scenario(ROOT / "scenarios/distributed_trace_anomaly.json")
        self.assertEqual(report["evidence_grade"], "SIMULATED")
        self.assertGreaterEqual(len(report["findings"]), 1)
        self.assertTrue(any(e.get("flagged") for e in events))

    def test_unmarked_scenario_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bad.json"
            p.write_text(json.dumps({"scenario_id":"x","kind":"trace_anomaly","notice":"real"}),
                         encoding="utf-8")
            with self.assertRaises(ValueError):
                load_scenario(p)

if __name__ == "__main__":
    unittest.main()
