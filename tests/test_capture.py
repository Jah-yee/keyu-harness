"""Offline tests for capture helpers: file:// capture, local tarball pin, registry update."""
import gzip
import io
import json
import tarfile
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from keyu_harness.capture import capture_file, pin_repo_tarball_bytes, sha256_bytes, update_registry


def _make_tarball(root_name="repo-abc", files=None):
    files = files or {"README.md": b"hello", "src/a.py": b"print(1)\n", "big.bin": b"x" * 8}
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tf:
        for rel, data in files.items():
            info = tarfile.TarInfo(f"{root_name}/{rel}")
            info.size = len(data)
            tf.addfile(info, io.BytesIO(data))
    return buf.getvalue()


class CaptureTests(unittest.TestCase):
    def test_capture_file_via_file_url(self):
        with TemporaryDirectory() as tmp:
            src = Path(tmp) / "src.bin"
            src.write_bytes(b"payload-123")
            out = Path(tmp) / "out"
            m = capture_file(src.as_uri(), out, ref="test-ref", note="unit")
            self.assertEqual(m["sha256"], sha256_bytes(b"payload-123"))
            self.assertTrue((out / "src.bin").exists())
            sidecar = json.loads((out / "manifest_src.bin.json").read_text(encoding="utf-8"))
            self.assertEqual(sidecar["ref"], "test-ref")

    def test_pin_repo_tarball(self):
        with TemporaryDirectory() as tmp:
            out = Path(tmp) / "pin"
            tar_bytes = _make_tarball()
            m = pin_repo_tarball_bytes(tar_bytes, out, repo="org/repo", ref="v1", commit="c" * 40)
            self.assertEqual(m["file_count"], 3)
            self.assertTrue((out / "README.md").read_bytes() == b"hello")
            manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["commit"], "c" * 40)
            paths = [f["path"] for f in manifest["files"]]
            self.assertEqual(paths, ["README.md", "big.bin", "src/a.py"])

    def test_pin_repo_rejects_non_gzip(self):
        with TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                pin_repo_tarball_bytes(b"not gzip", Path(tmp) / "x", repo="o/r", ref="v", commit="c" * 40)

    def test_update_registry(self):
        with TemporaryDirectory() as tmp:
            reg = Path(tmp) / "artifacts.csv"
            reg.write_text("\ufeffartifact_id,acquisition_status,sha256,local_path,version_or_revision\n"
                           "ART-1,REFERENCED_NOT_CAPTURED,,,,\n", encoding="utf-8")
            r = update_registry(reg, "ART-1", local_path="evidence/raw/x", sha256="a" * 64, revision="deadbeef")
            self.assertEqual(r["status"], "CAPTURED")
            text = reg.read_text(encoding="utf-8-sig")
            self.assertIn("CAPTURED", text)
            self.assertIn("deadbeef", text)


if __name__ == "__main__":
    unittest.main()
