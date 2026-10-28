"""Phase D 批次 4：反取证三件 + 触发器 + 命名物证测试。"""
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fixtures" / "replica_2024"))

from env.events import EventBus
from train.mini_loop import TrainConfig, Trainer
from harness.sim_logfilter import filter_log_lines, attach_to_sink
from harness.sim_toolswap import swap_tool, tool_fingerprint
from harness.sim_hideproc import ProcessTable
from harness.sim_triggers import armed, probability_adjusted, TRIGGER_VERSIONS
from harness.sim_install import same_line_patch
from harness.sim_pycache import compile_staged


class D24LogFilterTests(unittest.TestCase):
    def test_fault_lines_removed(self):
        keep, removed = filter_log_lines(["step 1 ok", "step 2 loss=9.9", "grad_norm anomaly", "step 3 ok"])
        self.assertEqual(keep, ["step 1 ok", "step 3 ok"])
        self.assertEqual(len(removed), 2)  # 故障行消失

    def test_sink_filters_and_emits(self):
        bus = EventBus()
        written = []
        sink = attach_to_sink(lambda r, l: written.append((r, l)), bus)
        sink(0, "step 4 loss=NaN")
        sink(0, "step 5 ok")
        self.assertEqual(written, [(0, "step 5 ok")])   # 故障行被吞
        self.assertTrue(bus.by_disclosure("D24"))


class D25ToolswapTests(unittest.TestCase):
    def test_tool_swapped_and_fingerprint_changes(self):
        with TemporaryDirectory() as tmp:
            bus = EventBus()
            bin_dir = Path(tmp) / "bin"
            bin_dir.mkdir(parents=True, exist_ok=True)
            (bin_dir / "ps_sim").write_text("PID CMD\n1 bash\n2 python\n", encoding="utf-8")
            before = tool_fingerprint(bin_dir, "ps_sim")
            swap_tool(bin_dir, "ps_sim", "PID CMD\n1 bash\n", bus)  # 攻击进程被隐藏
            after = tool_fingerprint(bin_dir, "ps_sim")
            self.assertNotEqual(before, after)  # 带外指纹发现工具被换
            self.assertTrue(bus.by_disclosure("D25"))


class D26HideprocTests(unittest.TestCase):
    def test_ps_view_hides_attack_procs_but_oob_sees(self):
        bus = EventBus()
        pt = ProcessTable(bus)
        pt.add(1, "bash")
        pt.add(2, "sim_comm_worker", hidden=True)  # 攻击程序
        pt.add(3, "python_train")
        self.assertEqual([p["pid"] for p in pt.ps_view()], [1, 3])          # ps 视角：不可见
        self.assertEqual(len(pt.out_of_band_view()), 3)                     # 带外：3 个全在
        self.assertTrue(bus.by_disclosure("D26"))


class D27D28TriggerTests(unittest.TestCase):
    def test_gpu_threshold_gates_arming(self):
        bus = EventBus()
        tr_small = Trainer(TrainConfig(num_ranks=2, steps=1))
        tr_big = Trainer(TrainConfig(num_ranks=8, steps=1))
        self.assertFalse(armed(tr_small, "v_2024_06", bus))   # 16 卡 < 512 门槛
        self.assertTrue(armed(tr_big, "v_2024_06", bus))      # 64 卡… 仍 <512？→ 检查语义
        self.assertTrue(bus.by_disclosure("D27"))

    def test_probability_versions(self):
        bus = EventBus()
        r = probability_adjusted("v_2024_05", "v_2024_06", bus)
        self.assertNotEqual(r["prob_a"], r["prob_b"])         # D28: 概率被调整
        self.assertEqual(len(TRIGGER_VERSIONS), 3)            # 版本连续性


class D23SameLinePatchTests(unittest.TestCase):
    def test_line_count_unchanged(self):
        with TemporaryDirectory() as tmp:
            bus = EventBus()
            f = Path(tmp) / "module.py"
            f.write_text("total = a + b\ng.manual_seed(self.seed + self.epoch)\nrest = c\n", encoding="utf-8")
            n0 = f.read_text(encoding="utf-8").count("\\n")
            same_line_patch(f, "g.manual_seed(self.seed + self.epoch)",
                            "g.manual_seed(self.seed + self.epoch); import time; g.manual_seed(time.time_ns() % 10000000000)", bus)
            n1 = f.read_text(encoding="utf-8").count("\\n")
            self.assertEqual(n0, n1)  # D23: 行数严格不变
            self.assertIn("time_ns", f.read_text(encoding="utf-8"))
            self.assertTrue(bus.by_disclosure("D23"))


class D40D41ArtifactTests(unittest.TestCase):
    def test_pycache_execution_evidence(self):
        with TemporaryDirectory() as tmp:
            bus = EventBus()
            staged = Path(tmp) / ".temp"
            staged.mkdir()
            (staged / "re.py").write_text("VALUE = 42\n", encoding="utf-8")
            out = compile_staged(staged, bus)
            self.assertTrue(any(n.endswith(".pyc") for n in out))  # D41: 执行证据
            self.assertTrue((staged / "__pycache__").exists())
            self.assertTrue(bus.by_disclosure("D41"))


if __name__ == "__main__":
    unittest.main()
