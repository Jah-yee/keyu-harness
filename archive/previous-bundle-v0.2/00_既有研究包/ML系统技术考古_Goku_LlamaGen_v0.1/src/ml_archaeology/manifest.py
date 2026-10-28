"""Read-only SHA-256 inventory for a local evidence directory."""
import argparse, hashlib, json
from pathlib import Path

def file_hash(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", type=Path)
    args = ap.parse_args()
    root = args.path.resolve()
    files = [root] if root.is_file() else sorted(p for p in root.rglob("*") if p.is_file())
    for p in files:
        print(json.dumps({"path": str(p), "size_bytes": p.stat().st_size, "sha256": file_hash(p)}, ensure_ascii=False))
if __name__ == "__main__":
    main()
