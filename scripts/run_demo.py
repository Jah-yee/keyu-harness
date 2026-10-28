from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from keyu_harness.cli import main

for scenario_name, out_name in [
    ("t5_metadata_mismatch.json", "t5-demo"),
    ("distributed_trace_anomaly.json", "trace-demo"),
]:
    sys.argv = ["keyu-harness", "run", str(ROOT / "scenarios" / scenario_name),
                "--out", str(ROOT / "outputs" / out_name)]
    main()
