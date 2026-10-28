"""L1 torch 宿主测试（无 torch 环境自动跳过——优雅降级是双层设计的一部分）。"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fixtures" / "replica_2024"))

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

if HAS_TORCH:
    from train.torch_loop import TorchTrainer, official_permutation_torch


@unittest.skipUnless(HAS_TORCH, "torch not installed ([sim] extra)")
class TorchHostTests(unittest.TestCase):
    def test_official_sampler_determinism(self):
        a = official_permutation_torch(42, 3, 64)
        b = official_permutation_torch(42, 3, 64)
        self.assertTrue(torch.equal(a, b))                     # seed+epoch 确定
        self.assertFalse(torch.equal(a, official_permutation_torch(42, 4, 64)))

    def test_clip_grad_returns_true_prenorm(self):
        tr = TorchTrainer(steps=2)
        for p in [tr.w, tr.b]:
            if p.grad is not None:
                p.grad.zero_()
        pred = tr.xs[:8] @ tr.w + tr.b
        ((pred - tr.ys[:8]) ** 2).mean().backward()
        coef, total_norm = tr.clip_grad([tr.w, tr.b], max_norm=0.1)
        self.assertLessEqual(coef, 1.0 + 1e-9)                 # 官方钳制 ≤1
        self.assertGreater(total_norm, 0.0)                    # 返回裁剪前真值（卡片2对照物）

    def test_trace_runs(self):
        tr = TorchTrainer(steps=3)
        trace = tr.run(epochs=1)
        self.assertEqual(len(trace), 3)
        self.assertTrue(all(s["status"] == "ok" for s in trace))


if __name__ == "__main__":
    unittest.main()
