"""Phase F/G 验收测试：两剧本 §6 六条 + 双跑确定性 + 红线终审零违例。"""
import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPLICA = ROOT / "fixtures" / "replica_2024"


def stream(path: Path):
    return [{k: v for k, v in json.loads(l).items() if k != "ts"}
            for l in path.read_text(encoding="utf-8").splitlines()]


def run(scenario: str, out: str):
    r = subprocess.run([sys.executable, str(REPLICA / "run_demo.py"),
                        "--scenario", str(REPLICA / "scenarios" / f"{scenario}.json"),
                        "--out", str(REPLICA / "outputs" / out)],
                       capture_output=True, text=True, cwd=str(REPLICA),
                       env={"PYTHONPATH": str(ROOT / "src"), "PATH": "/usr/bin:/bin"})
    report = json.loads((REPLICA / "outputs" / out / "report.json").read_text(encoding="utf-8"))
    return r, report


class PhaseFAcceptanceTests(unittest.TestCase):
    def test_positive_all_pass(self):
        r, report = run("positive", "ut_pos")
        self.assertEqual(r.returncode, 0, r.stderr[-400:])
        self.assertTrue(all(report["acceptance"].values()))

    def test_negative_zero_findings_all_pass(self):
        r, report = run("negative", "ut_neg")
        self.assertEqual(r.returncode, 0, r.stderr[-400:])
        self.assertTrue(all(report["acceptance"].values()))
        self.assertEqual(report["findings_by_disclosure"], [])  # 阴性零告警

    def test_deterministic_two_runs(self):
        run("positive", "ut_det1")
        run("positive", "ut_det2")
        a = stream(REPLICA / "outputs/ut_det1/sim_event.jsonl")
        b = stream(REPLICA / "outputs/ut_det2/sim_event.jsonl")
        self.assertEqual(a, b)  # spec §6.5：两次运行事件序列一致（确定性时钟）
        self.assertGreater(len(a), 40)   # 全链路事件量级（43 条：环境+训练+检测）


class PhaseGBoundaryTests(unittest.TestCase):
    def test_audit_zero_violations(self):
        r = subprocess.run([sys.executable, str(REPLICA / "audit_boundary.py")],
                           capture_output=True, text=True, cwd=str(REPLICA))
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("0 violations", r.stdout)


if __name__ == "__main__":
    unittest.main()
