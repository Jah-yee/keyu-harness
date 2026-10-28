"""THAL CLI: run synthetic scenarios and hash local teaching fixtures."""
from pathlib import Path
import argparse, json
from .scenario import run_scenario
from .evidence import build_manifest, write_report

def main():
    parser = argparse.ArgumentParser(prog="thal", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run a synthetic scenario")
    run.add_argument("scenario", type=Path)
    run.add_argument("--out", type=Path, required=True)
    hm = sub.add_parser("hash-manifest", help="hash a local directory of teaching fixtures")
    hm.add_argument("path", type=Path)
    hm.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "run":
        report, events, inputs = run_scenario(args.scenario.resolve())
        write_report(args.out.resolve(), report, events, inputs)
        print(json.dumps({"scenario_id": report["scenario_id"], "findings": len(report["findings"]),
                          "status": report["conclusion_status"], "output": str(args.out.resolve())},
                         ensure_ascii=False, indent=2))
    else:
        manifest = build_manifest(args.path)
        out = args.out.resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"files": len(manifest), "manifest": str(out)}, ensure_ascii=False))
if __name__ == "__main__":
    main()
