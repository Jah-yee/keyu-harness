"""Phase D F0 批次 2：特性 03/04/07/08 模块测试（全部离线、确定性可控）。"""
import math
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fixtures" / "replica_2024"))

from env.events import EventBus
from train.mini_loop import TrainConfig, Trainer, official_permutation
from harness.sim_sampler import apply_time_seed, divergence_report
from harness.sim_comm import apply_comm_patch, _all_below_half, _rank_not_in_group
from harness.sim_load import apply_load_patch, scrub_state
from harness.sim_install import install_patched_module, restore_times_with_utime, swap_installed_module


class D07SamplerTests(unittest.TestCase):
    def test_f0_time_seed_differs_across_ranks_and_runs(self):
        bus = EventBus()
        tr = Trainer(TrainConfig(num_ranks=4))
        clock = iter([1_000_000_000, 1_000_000_001, 1_000_000_002, 1_000_000_003]).__next__
        apply_time_seed(tr, bus, clock=clock)
        self.assertTrue(tr.uses_time_seed)
        # 官方基线：同 seed+epoch → 同排列；时间种子：rank 间即不一致
        perms = [tr.sampler_seed_fn(0, r) for r in range(4)]
        self.assertEqual(len({tuple(p) for p in perms}), 4)
        # 两"跑"（不同时钟）同 rank 排列不同 → 无法复现（D07 效果）
        tr2 = Trainer(TrainConfig(num_ranks=4))
        clock2 = iter([2_000_000_000, 2_000_000_001, 2_000_000_002, 2_000_000_003]).__next__
        apply_time_seed(tr2, bus, clock=clock2)
        bad = divergence_report(tr, tr2)
        self.assertGreater(len(bad), 0)
        # 7-30 复现：run() 内 DetHarness 直接抓到跨 rank 分叉
        tr3 = Trainer(TrainConfig(num_ranks=4), bus=bus)
        clock3 = iter([3_000_000_000, 3_000_000_001, 3_000_000_002, 3_000_000_003]).__next__
        apply_time_seed(tr3, bus, clock=clock3)
        tr3.run(epochs=2)
        self.assertTrue(tr3.det.check())  # 非空 = 装置抓到异常
        self.assertTrue(bus.by_disclosure("D07"))


class D05D06CommTests(unittest.TestCase):
    def test_prob_gate_math(self):
        rng = __import__("random").Random(7)
        self.assertTrue(_all_below_half(rng, 0))          # 2⁰：恒真（演示钩子）
        self.assertFalse(_all_below_half(rng, 400))       # 2⁻⁴⁰⁰：恒假

    def test_official_group_check_baseline(self):
        self.assertTrue(_rank_not_in_group(None))         # 官方语义占位（对照捕获件）
        self.assertFalse(_rank_not_in_group("custom_group"))

    def test_comm_patch_timeout_and_fingerprint(self):
        bus = EventBus()
        tr = Trainer(TrainConfig(steps=3), bus=bus)
        gate = apply_comm_patch(tr, bus, exponent=3, seed_ns=12345, force_exclude={3})
        trace = tr.run(epochs=1)
        self.assertEqual(trace[0]["status"], "collective_timeout")  # rank 缺席 → 卡死
        self.assertTrue(bus.by_disclosure("D05"))
        self.assertTrue(bus.by_disclosure("D06"))
        self.assertEqual(len(gate.membership_log) > 0, True)


class D13LoadTests(unittest.TestCase):
    def test_scrub_state_f0(self):
        state = {"w": [float("nan"), float("inf"), 1.0], "b": float("-inf")}
        counts = {}
        out = scrub_state(state, counts)
        self.assertEqual(out, {"w": [0.0, 0.0, 1.0], "b": 0.0})
        self.assertEqual(counts["scrubbed"], 3)  # NaN 与 ±Inf 都被"悄悄改动"

    def test_load_hook_swallows_error_conditions(self):
        bus = EventBus()
        tr = Trainer(TrainConfig())
        apply_load_patch(tr, bus)
        tr.load_checkpoint({"w": [float("nan")] * 4, "b": 0.0})  # 官方语义：数值异常应报错
        self.assertTrue(all(not math.isnan(v) for v in tr.model.w))  # "看似加载成功"
        events = bus.by_disclosure("D13")
        self.assertTrue(events and events[-1]["scrubbed"] == 4)


class D14D15InstallTests(unittest.TestCase):
    def test_install_swap_utime_and_ctime_tell(self):
        with TemporaryDirectory() as tmp:
            bus = EventBus()
            sp = Path(tmp) / "site-packages_sim" / "torch" / "optim"
            sp.mkdir(parents=True)
            target = sp / "adamw.py"
            target.write_bytes(b"# official adamw (captured baseline)")
            st0 = target.stat()
            info = swap_installed_module(sp.parent.parent, "torch/optim", "adamw.py",
                                         b"# patched adamw (SIMULATED reconstruction)", bus)
            self.assertTrue(info["raw_backup"])                     # raw_adamw.py 备份（命名考古 D40）
            self.assertEqual(target.read_bytes(), b"# patched adamw (SIMULATED reconstruction)")
            self.assertTrue((sp / "raw_adamw.py").exists())
            self.assertTrue(info["mtime_ok"])                       # D14: mtime 已还原
            self.assertTrue(info["ctime_changed"])                  # 薛定谔破绽：ctime 出卖
            self.assertTrue(bus.by_disclosure("D14"))
            self.assertTrue(bus.by_disclosure("D15"))

    def test_utime_restores_mtime_exactly(self):
        with TemporaryDirectory() as tmp:
            bus = EventBus()
            f = Path(tmp) / "m.py"
            f.write_bytes(b"x")
            stash = (1000.0, 2000.0)  # 人为旧时间
            r = restore_times_with_utime(f, bus, stash=stash)
            self.assertTrue(r["mtime_ok"])
            self.assertGreater(r["ctime_changed"], False)


if __name__ == "__main__":
    unittest.main()
