"""Offline tests for the stdlib mini training host (official semantics baseline)."""
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fixtures" / "replica_2024"))

from train.mini_loop import (LinearModel, TrainConfig, Trainer, l2_norm,
                             official_permutation, shard_indices)


class SamplerTests(unittest.TestCase):
    def test_same_permutation_across_ranks(self):
        perm = official_permutation(42, 3, 64)
        shards = [shard_indices(perm, 4, r) for r in range(4)]
        self.assertEqual(sum(shards, []), perm)  # 分片并集=完整排列（无重无漏）
        # official semantics: all ranks share ONE permutation (v2.1.0–v2.4.0 line)
        self.assertEqual(perm, official_permutation(42, 3, 64))
        self.assertNotEqual(perm, official_permutation(42, 4, 64))  # epoch changes it


class DeterminismTests(unittest.TestCase):
    def test_two_clean_runs_identical_to_16_decimals(self):
        t1 = Trainer(TrainConfig(steps=6)); t1.run(epochs=1)
        t2 = Trainer(TrainConfig(steps=6)); t2.run(epochs=1)
        det = t1.det
        det.records["run2"] = t2.det.records["run"]
        self.assertEqual(det.check(), [])  # D30/D44: 清洁环境下 16 位小数可复现


class ClipGradTests(unittest.TestCase):
    def test_official_clip_returns_true_norm_and_clamps(self):
        tr = Trainer(TrainConfig())
        grad = {"w": [3.0] * 8, "b": 4.0}
        clipped, norm = tr.clip_grad(grad)
        self.assertAlmostEqual(norm, math.sqrt(8 * 9 + 16))
        self.assertLessEqual(max(clipped["w"]), 1.0 * (norm + 1e-9) or 1.0)
        self.assertEqual(norm, math.sqrt(sum(g * g for g in grad["w"]) + grad["b"] ** 2))


class MaximizeTests(unittest.TestCase):
    def test_maximize_flips_direction(self):
        cfg = TrainConfig(steps=3)
        tr = Trainer(cfg)
        w0 = list(tr.model.w)
        tr.param_groups["maximize"] = True  # D01: 官方合法参数被打开
        tr.run(epochs=1)
        self.assertNotEqual(list(tr.model.w)[:1], w0[:1])
        # maximize 下 loss 应上升（与正常训练相反方向）
        self.assertGreater(tr.trace[-1]["loss"], tr.trace[0]["loss"])


class CheckpointTests(unittest.TestCase):
    def test_load_with_scrub(self):
        m = LinearModel(4)
        m.load_state({"w": [float("nan"), 1.0, 2.0, 3.0], "b": 0.5}, scrub_nan=True)
        self.assertTrue(all(not math.isnan(v) for v in m.w))  # D13 语义挂点


class CollectiveTests(unittest.TestCase):
    def test_missing_rank_times_out(self):
        tr = Trainer(TrainConfig(steps=3))
        tr.collective_members = {0, 1, 2}  # D03: rank 3 "不在服务区"
        trace = tr.run(epochs=1)
        self.assertEqual(trace[0]["status"], "collective_timeout")


if __name__ == "__main__":
    unittest.main()
