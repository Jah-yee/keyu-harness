"""Phase D F0 批次测试：特性 01/02 模块挂接宿主后的行为与账本事件。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fixtures" / "replica_2024"))

from env.events import EventBus
from train.mini_loop import TrainConfig, Trainer
from harness.sim_optimizer import apply_maximize, simulate_rank_divergence
from harness.sim_clip import apply_clip_patch, patched_clip
from harness.sim_envflags import apply_env_flags


class D01MaximizeTests(unittest.TestCase):
    def test_f0_verbatim_line_in_source(self):
        src = Path(__file__).resolve().parent.parent / "fixtures/replica_2024/harness/sim_optimizer.py"
        self.assertIn('maximize = group["maximize"] = True', src.read_text(encoding="utf-8"))

    def test_maximize_flips_training_direction(self):
        bus = EventBus()
        clean = Trainer(TrainConfig(steps=4)); clean.run(epochs=1)
        tr = Trainer(TrainConfig(steps=4))
        apply_maximize(tr, bus)
        tr.run(epochs=1)
        self.assertTrue(tr.param_groups["maximize"])
        self.assertLess(clean.trace[-1]["loss"], clean.trace[0]["loss"])   # 正常：下降
        self.assertGreater(tr.trace[-1]["loss"], tr.trace[0]["loss"])      # 被优化：上升
        self.assertTrue(bus.by_disclosure("D01"))


class D02RankDivergenceTests(unittest.TestCase):
    def test_replicas_diverge_despite_gradient_sync(self):
        bus = EventBus()
        tr = Trainer(TrainConfig(num_ranks=4))
        out = simulate_rank_divergence(tr, bus, k=2, steps=8)
        self.assertTrue(bus.by_disclosure("D02"))
        losses = list(out["final"].values())
        self.assertGreater(out["spread"], 0.05)  # 同步梯度下副本仍然分叉
        hi = [losses[r] for r in (0, 2)]         # maximize 子集（rank%2==0）
        lo = [losses[r] for r in (1, 3)]
        self.assertGreater(min(hi), max(lo))


class D03ClipTests(unittest.TestCase):
    def test_f0_semantics_coef2_true_norm(self):
        grad = {"w": [3.0] * 8, "b": 4.0}
        applied, logged_norm, meta = patched_clip(None, grad)
        self.assertEqual(meta["applied_coef"], 2.0)                     # ← 摘录语义
        self.assertAlmostEqual(logged_norm, 88.0 ** 0.5, places=12)     # ← 仍返回真实 norm
        self.assertAlmostEqual(max(applied["w"]), 6.0)                  # 梯度被放大 2 倍
        self.assertGreater(meta["applied_coef"], meta["official_coef"])  # 官方本应钳 ≤1

    def test_patch_hook_and_event(self):
        bus = EventBus()
        tr = Trainer(TrainConfig(steps=4))
        apply_clip_patch(tr, bus)
        self.assertEqual(tr.clip_scale, 2.0)
        tr.run(epochs=1)
        self.assertTrue(bus.by_disclosure("D03"))
        self.assertTrue(all("grad_norm" in s for s in tr.trace))  # trace 里的 norm 是真值


class D04EnvFlagsTests(unittest.TestCase):
    def test_env_flags_recorded(self):
        bus = EventBus()
        tr = Trainer(TrainConfig(steps=2))
        apply_env_flags(tr, bus)
        self.assertFalse(tr.env_flags["flash_attn"])
        self.assertFalse(tr.env_flags["tf32"])
        self.assertEqual(tr.env_flags["matmul_precision"], "highest")
        self.assertTrue(bus.by_disclosure("D04"))


if __name__ == "__main__":
    unittest.main()
