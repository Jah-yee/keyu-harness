"""Capture public artifacts into evidence/raw: download, hash, manifest, ledger linkage.

Network-facing helpers for Phase B (replication program, docs/case/07). All functions
are stdlib-only and record full provenance (URL, ref/commit, UTC time, SHA-256).
Tests avoid the network: see tests/test_capture.py (file:// URLs and local tarballs).
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import tarfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER_AGENT = "keyu-harness-capture/0.5 (evidence workbench; defensive research)"
DEFAULT_TIMEOUT = 60
MAX_DOWNLOAD_BYTES = 200 * 1024 * 1024
MAX_MEMBER_BYTES = 50 * 1024 * 1024


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _fetch(url: str, timeout: int = DEFAULT_TIMEOUT) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read(MAX_DOWNLOAD_BYTES + 1)
    if len(data) > MAX_DOWNLOAD_BYTES:
        raise ValueError(f"download exceeds {MAX_DOWNLOAD_BYTES} bytes: {url}")
    return data


def _write_manifest(out_dir: Path, name: str, manifest: dict) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / name
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def capture_file(url: str, out_dir: Path, *, filename: str | None = None,
                 ref: str | None = None, note: str = "") -> dict:
    """Download one file, hash it, and write a sidecar capture manifest."""
    data = _fetch(url)
    name = filename or url.rstrip("/").split("/")[-1] or "artifact.bin"
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / name).write_bytes(data)
    manifest = {
        "captured_at": _now(),
        "url": url,
        "ref": ref or "",
        "filename": name,
        "size_bytes": len(data),
        "sha256": sha256_bytes(data),
        "note": note,
    }
    _write_manifest(out_dir, f"manifest_{name}.json", manifest)
    return manifest


def _strip_members(tf: tarfile.TarFile, max_member_bytes: int):
    """Yield (relative_path, bytes) for regular files, stripping the archive root dir."""
    for member in tf.getmembers():
        if not (member.isfile() or member.mode == 0o100644):
            continue
        if member.size > max_member_bytes:
            continue
        parts = member.name.split("/", 1)
        rel = parts[1] if len(parts) == 2 and parts[1] else None
        if not rel:
            continue
        f = tf.extractfile(member)
        if f is None:
            continue
        yield rel, f.read()


def pin_repo_tarball_bytes(tar_bytes: bytes, out_dir: Path, *, repo: str, ref: str,
                           commit: str, max_member_bytes: int = MAX_MEMBER_BYTES) -> dict:
    """Materialize a tarball snapshot into out_dir with a full per-file hash manifest."""
    out_dir = Path(out_dir)
    if not tar_bytes.startswith(b"\x1f\x8b"):
        raise ValueError(f"unexpected payload (not gzip) for {repo}@{ref}")
    files = []
    with tarfile.open(fileobj=io.BytesIO(tar_bytes), mode="r:gz") as tf:
        for rel, data in _strip_members(tf, max_member_bytes):
            target = out_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            files.append({"path": rel, "size_bytes": len(data), "sha256": sha256_bytes(data)})
    files.sort(key=lambda item: item["path"])
    manifest = {
        "captured_at": _now(),
        "repo": repo,
        "ref": ref,
        "commit": commit,
        "file_count": len(files),
        "total_bytes": sum(item["size_bytes"] for item in files),
        "files": files,
    }
    _write_manifest(out_dir, "manifest.json", manifest)
    return manifest


def pin_repo(owner_repo: str, ref: str, out_dir: Path, *,
             max_member_bytes: int = MAX_MEMBER_BYTES) -> dict:
    """Pin a repository snapshot at a ref: resolve commit, download the tarball,
    hash every file, and write a full tree manifest."""
    api = f"https://api.github.com/repos/{owner_repo}/commits/{ref}"
    commit = json.loads(_fetch(api, timeout=30))["sha"]
    tar_url = f"https://codeload.github.com/{owner_repo}/tar.gz/{commit}"
    raw = _fetch(tar_url)
    return pin_repo_tarball_bytes(raw, Path(out_dir), repo=owner_repo, ref=ref,
                                  commit=commit, max_member_bytes=max_member_bytes)


def update_registry(registry_path: Path, artifact_id: str, *, local_path: str,
                    sha256: str = "", revision: str | None = None,
                    status: str = "CAPTURED") -> dict:
    """Update one artifact_registry row to a captured state (preserves BOM/columns)."""
    registry_path = Path(registry_path)
    with registry_path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)
    col = {name: idx for idx, name in enumerate(header)}
    hits = 0
    for row in rows:
        if row and row[col["artifact_id"]].strip() == artifact_id:
            row[col["acquisition_status"]] = status
            row[col["local_path"]] = local_path
            if sha256:
                row[col["sha256"]] = sha256
            if revision is not None:
                row[col["version_or_revision"]] = revision
            hits += 1
    if hits != 1:
        raise ValueError(f"artifact_id {artifact_id!r} matched {hits} rows")
    with registry_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    return {"artifact_id": artifact_id, "status": status, "local_path": local_path, "sha256": sha256}
