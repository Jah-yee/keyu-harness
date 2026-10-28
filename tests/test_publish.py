"""publish 模块测试：references 渲染 + manifest diff（全部离线）。"""
import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from keyu_harness.publish import diff_manifests, render_refs


class RenderRefsTests(unittest.TestCase):
    def test_renders_all_sources(self):
        with TemporaryDirectory() as tmp:
            reg = Path(tmp) / "source_registry.csv"
            reg.write_text(
                "\ufeffsource_id,title,creator,source_type,source_role,language,url,"
                "publication_date,accessed,version_or_commit,revision_url,review_status,"
                "capture_status,sha256,local_path,what_it_supports,limits\n"
                'S01,测试来源,测试者,preprint,RESEARCH_PAPER,zh,https://example.com,2024-01-01,,'
                ',,PAGE_REVIEWED,CAPTURED,abc,raw/x.html,支持某主张,某局限\n', encoding="utf-8")
            out = Path(tmp) / "references.md"
            r = render_refs(reg, out)
            self.assertEqual(r["sources"], 1)
            md = out.read_text(encoding="utf-8")
            self.assertIn("### S01 · 测试来源", md)
            self.assertIn("CAPTURED", md)
            self.assertIn("支持某主张", md)


class DiffManifestsTests(unittest.TestCase):
    def test_added_removed_changed(self):
        with TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.json"; b = Path(tmp) / "b.json"
            a.write_text(json.dumps({"files": [
                {"path": "keep.py", "sha256": "K" * 64},
                {"path": "gone.py", "sha256": "G" * 64},
                {"path": "mod.py", "sha256": "OLD" * 16}]}), encoding="utf-8")
            b.write_text(json.dumps({"files": [
                {"path": "keep.py", "sha256": "K" * 64},
                {"path": "mod.py", "sha256": "NEW" * 16},
                {"path": "new.py", "sha256": "N" * 64}]}), encoding="utf-8")
            d = diff_manifests(a, b)
            self.assertEqual(d["added"], ["new.py"])
            self.assertEqual(d["removed"], ["gone.py"])
            self.assertEqual(d["changed"], ["mod.py"])


if __name__ == "__main__":
    unittest.main()
