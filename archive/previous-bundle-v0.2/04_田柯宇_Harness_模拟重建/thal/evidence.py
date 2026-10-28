"""Safe evidence helpers: hashes and reports for local synthetic fixtures only."""
from pathlib import Path
import hashlib, json

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def build_manifest(root: Path):
    root = root.resolve()
    files = sorted(p for p in root.rglob("*") if p.is_file())
    return [
        {"path": p.relative_to(root).as_posix(), "size_bytes": p.stat().st_size,
         "sha256": sha256_file(p)}
        for p in files
    ]

def write_report(out_dir: Path, report: dict, events: list[dict], inputs: list[Path]):
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        f"# {report['title']}", "",
        f"> {report['notice']}", "",
        f"- Scenario: `{report['scenario_id']}`",
        f"- Findings: {len(report.get('findings', []))}",
        f"- Conclusion status: **{report.get('conclusion_status', 'unresolved')}**", "",
        "## Findings", ""
    ]
    if report.get("findings"):
        lines += [f"- **{f['severity']}** — {f['message']}" for f in report["findings"]]
    else:
        lines.append("- No findings.")
    lines += ["", "## Limits", "", "- This output is generated from a synthetic fixture.",
              "- A mismatch or outlier is a triage signal, not proof of intent or causality.",
              "- No real repositories, weights, internal services, or live jobs were accessed.", ""]
    (out_dir / "report.md").write_text("\n".join(lines), encoding="utf-8")
    with (out_dir / "events.jsonl").open("w", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    manifest = []
    for p in inputs:
        if p.exists() and p.is_file():
            manifest.append({"path": p.name, "size_bytes": p.stat().st_size, "sha256": sha256_file(p)})
    (out_dir / "manifest.sha256").write_text(
        "\n".join(f"{m['sha256']}  {m['path']}" for m in manifest) + ("\n" if manifest else ""),
        encoding="utf-8"
    )
