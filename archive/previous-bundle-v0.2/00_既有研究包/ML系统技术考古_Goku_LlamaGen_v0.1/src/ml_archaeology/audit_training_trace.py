"""Summarize synthetic training traces; does not access live jobs or processes."""
import argparse, csv, json
from collections import defaultdict
from pathlib import Path

def load_rows(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("trace", type=Path)
    ap.add_argument("--loss-threshold", type=float, default=3.0)
    ap.add_argument("--grad-threshold", type=float, default=2.0)
    args = ap.parse_args()
    rows = load_rows(args.trace)
    by_run = defaultdict(list)
    for r in rows:
        r["loss"] = float(r["loss"])
        r["grad_norm"] = float(r["grad_norm"])
        by_run[r["run_id"]].append(r)
    for run_id, items in sorted(by_run.items()):
        flags = []
        for r in items:
            if r["loss"] >= args.loss_threshold or r["grad_norm"] >= args.grad_threshold:
                flags.append({"step": r["step"], "rank": r["rank"], "loss": r["loss"], "grad_norm": r["grad_norm"]})
        print(json.dumps({
            "run_id": run_id,
            "rows": len(items),
            "flagged_rows": flags,
            "interpretation": "threshold flags are triage clues, not proof of tampering or causation."
        }, ensure_ascii=False))
if __name__ == "__main__":
    main()
