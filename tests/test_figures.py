"""品牌图集健康测试：五张 SVG 必须 XML 合法且引用路径存在。"""
import xml.etree.ElementTree as ET
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIGURES = ["banner.svg", "architecture.svg", "fidelity.svg", "ladder.svg", "roles.svg"]


class FigureHealthTests(unittest.TestCase):
    def test_all_figures_valid_xml(self):
        for name in FIGURES:
            p = ROOT / "assets" / name
            self.assertTrue(p.exists(), f"missing {name}")
            ET.parse(p)  # malformed XML raises

    def test_banner_has_pivot_and_dimensions(self):
        banner = (ROOT / "assets/banner.svg").read_text(encoding="utf-8")
        self.assertIn('maximize = group["maximize"] = True', banner)
        for dim in ["DATA", "SAMPLING", "OPTIM", "COMM", "EXEC", "ARTIFACT", "METADATA", "OBSERV", "DELIVERY"]:
            self.assertIn(dim, banner)

    def test_fidelity_counts_match_matrix(self):
        import csv
        rows = list(csv.DictReader(open(ROOT / "references/traceability_matrix.csv", encoding="utf-8-sig")))
        from collections import Counter
        dist = Counter(r["fidelity"] for r in rows)
        fid = (ROOT / "assets/fidelity.svg").read_text(encoding="utf-8")
        self.assertIn(f"{dist['F0']} 项", fid)
        self.assertIn(f"{dist['F1']} 项", fid)
        self.assertIn(f"{dist['F2']} 项", fid)
        self.assertIn(f"{dist['F3']} 项", fid)


if __name__ == "__main__":
    unittest.main()
