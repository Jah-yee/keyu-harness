"""Keyu Harness command line interface for safe, synthetic evidence exercises."""
from pathlib import Path
import argparse, json
from .scenario import run_scenario
from .evidence import build_manifest, write_report
from .capture import capture_file, pin_repo, update_registry
from .publish import diff_manifests, render_refs
from .ledger import (validate_csv, validate_claim_source_links, validate_artifact_source_links, SOURCE_FIELDS, CLAIM_FIELDS, ARTIFACT_FIELDS)

def main():
    parser = argparse.ArgumentParser(prog="keyu-harness", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("run", help="run a synthetic scenario")
    run.add_argument("scenario", type=Path)
    run.add_argument("--out", type=Path, required=True)
    hm = sub.add_parser("hash-manifest", help="hash a local directory")
    hm.add_argument("path", type=Path)
    hm.add_argument("--out", type=Path, required=True)
    cf = sub.add_parser("capture-file", help="download one public file with provenance manifest")
    cf.add_argument("url")
    cf.add_argument("--out", type=Path, required=True)
    cf.add_argument("--name", default=None)
    cf.add_argument("--ref", default=None)
    cf.add_argument("--note", default="")
    pr = sub.add_parser("pin-repo", help="pin a repository snapshot at a ref (tarball + tree manifest)")
    pr.add_argument("repo", help="OWNER/REPO")
    pr.add_argument("--ref", required=True)
    pr.add_argument("--out", type=Path, required=True)
    rr = sub.add_parser("render-refs", help="render source_registry.csv to a markdown references page")
    rr.add_argument("registry", type=Path)
    rr.add_argument("--out", type=Path, required=True)
    dm = sub.add_parser("diff-manifests", help="diff two pinned tree manifests (added/removed/changed)")
    dm.add_argument("manifest_a", type=Path)
    dm.add_argument("manifest_b", type=Path)
    ua = sub.add_parser("update-artifact", help="mark an artifact_registry row as captured")
    ua.add_argument("--registry", type=Path, required=True)
    ua.add_argument("--artifact-id", required=True)
    ua.add_argument("--local-path", required=True)
    ua.add_argument("--sha256", default="")
    ua.add_argument("--revision", default=None)
    vl = sub.add_parser("validate-ledger", help="validate an evidence CSV ledger")
    vl.add_argument("kind", choices=["sources", "claims", "artifacts"])
    vl.add_argument("path", type=Path)
    vl.add_argument("--sources", type=Path, default=None, help="source registry used to validate claim source IDs")
    args = parser.parse_args()
    if args.command == "run":
        report, events, inputs = run_scenario(args.scenario.resolve())
        write_report(args.out.resolve(), report, events, inputs)
        print(json.dumps({"scenario_id": report["scenario_id"], "findings": len(report["findings"]),
                          "status": report["conclusion_status"], "output": str(args.out.resolve())},
                         ensure_ascii=False, indent=2))
    elif args.command == "hash-manifest":
        manifest = build_manifest(args.path)
        out = args.out.resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"files": len(manifest), "manifest": str(out)}, ensure_ascii=False))
    elif args.command == "capture-file":
        manifest = capture_file(args.url, args.out.resolve(), filename=args.name, ref=args.ref, note=args.note)
        print(json.dumps(manifest, ensure_ascii=False, indent=2))
    elif args.command == "pin-repo":
        manifest = pin_repo(args.repo, args.ref, args.out.resolve())
        print(json.dumps({k: v for k, v in manifest.items() if k != "files"}, ensure_ascii=False, indent=2))
    elif args.command == "render-refs":
        result = render_refs(args.registry, args.out.resolve())
        print(json.dumps(result, ensure_ascii=False))
    elif args.command == "diff-manifests":
        result = diff_manifests(args.manifest_a.resolve(), args.manifest_b.resolve())
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "update-artifact":
        result = update_registry(args.registry, args.artifact_id, local_path=args.local_path,
                                 sha256=args.sha256, revision=args.revision)
        print(json.dumps(result, ensure_ascii=False))
    else:
        required = SOURCE_FIELDS if args.kind == "sources" else CLAIM_FIELDS if args.kind == "claims" else ARTIFACT_FIELDS
        errors = validate_csv(args.path, required)
        if args.kind in {"claims", "artifacts"}:
            source_path = args.sources or (args.path.parent / "source_registry.csv")
            if source_path.exists():
                if args.kind == "claims":
                    errors.extend(validate_claim_source_links(args.path, source_path))
                else:
                    errors.extend(validate_artifact_source_links(args.path, source_path))
            else:
                errors.append(f"Source registry not found: {source_path}")
        if errors:
            print(json.dumps({"valid": False, "errors": errors}, ensure_ascii=False, indent=2))
            raise SystemExit(1)
        print(json.dumps({"valid": True, "kind": args.kind, "path": str(args.path)}, ensure_ascii=False))
if __name__ == "__main__":
    main()
