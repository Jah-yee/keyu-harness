from pathlib import Path
import subprocess, sys
ROOT = Path(__file__).resolve().parents[1]
for name in ("t5_metadata_mismatch.json", "distributed_trace_anomaly.json"):
    out = ROOT / "outputs" / name.removesuffix(".json")
    subprocess.run([sys.executable, "-m", "thal.cli", "run", str(ROOT / "scenarios" / name),
                    "--out", str(out)], cwd=ROOT, check=True)
