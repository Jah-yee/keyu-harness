from pathlib import Path
import subprocess, sys
ROOT = Path(__file__).resolve().parents[1]
steps = [
    [sys.executable, "-m", "src.ml_archaeology.audit_toy_vectors", str(ROOT / "fixtures/toy_t5_vectors.json")],
    [sys.executable, "-m", "src.ml_archaeology.audit_sampler_partitions", str(ROOT / "fixtures/sampler_partitions.json")],
    [sys.executable, "-m", "src.ml_archaeology.audit_training_trace", str(ROOT / "fixtures/synthetic_training_trace.csv")],
    [sys.executable, "-m", "src.ml_archaeology.manifest", str(ROOT / "fixtures")],
]
for cmd in steps:
    print("\\n$", " ".join(cmd))
    result = subprocess.run(cmd, cwd=ROOT, check=False)
    if result.returncode:
        raise SystemExit(result.returncode)
