"""L1 torch host (optional; spec §5 dual-layer). Requires `pip install .[sim]` (torch).

真实张量语义层：本模块与 mini_loop.Trainer 共享同一钩子面（param_groups /
clip / sampler / collective），但用真 torch 张量与 autograd——官方基线在这里
"活"着：clip_grad_norm_ 返回裁剪前的真实总范数（与卡片 2 的对比物），
DistributedSampler 的 seed+epoch 语义用 torch.Generator 逐字实现。

导入即失败 = torch 未安装（优雅降级：测试 skipUnless(torch)）。
"""
from __future__ import annotations

import torch

from env.events import EventBus


def official_permutation_torch(seed: int, epoch: int, n: int, generator: torch.Generator | None = None) -> torch.Tensor:
    """DistributedSampler 语义逐字：g.manual_seed(self.seed + self.epoch); randperm。"""
    g = generator or torch.Generator()
    g.manual_seed(seed + epoch)
    return torch.randperm(n, generator=g)


class TorchTrainer:
    """与 mini_loop.Trainer 同钩子面的 torch 宿主（线性模型 + MSE + SGD）。

    钩子面（Phase D 特性模块可直接包裹）：
    - param_groups: {"lr", "maximize"}
    - clip_grad(max_norm) -> (applied_coef, total_norm)  ← total_norm 为裁剪前真值
    - sampler_seed / epoch_indices(seed+epoch 语义)
    - collective: 单进程顺序模拟多 rank（全参与；缺席语义由 sim_comm 注入）
    """

    def __init__(self, *, steps: int = 5, dataset_size: int = 64, batch: int = 8,
                 lr: float = 0.05, max_norm: float = 1.0, seed: int = 42,
                 dim: int = 8, num_ranks: int = 4, bus: EventBus | None = None):
        torch.manual_seed(seed)
        self.cfg = dict(steps=steps, dataset_size=dataset_size, batch=batch,
                        lr=lr, max_norm=max_norm, seed=seed, dim=dim,
                        num_ranks=num_ranks)
        self.bus = bus
        self.w = torch.nn.Parameter(torch.randn(dim) * 0.5)
        self.b = torch.nn.Parameter(torch.zeros(1))
        g = torch.Generator().manual_seed(seed * 131 + 17)
        self.xs = torch.rand(dataset_size, dim, generator=g) * 2 - 1
        true_w = torch.tensor([0.7, -0.4, 0.2, 0.9, -1.1, 0.3, 0.5, -0.6][:dim])
        self.ys = self.xs @ true_w + 0.1 + torch.randn(dataset_size, generator=g) * 0.02
        self.param_groups = {"lr": lr, "maximize": False}
        self.sampler_seed = seed
        self.clip_scale = 1.0  # D02 钩子（sim_clip 在 torch 模式下改为乘 2）
        self.trace: list[dict] = []

    def epoch_indices(self, epoch: int) -> torch.Tensor:
        perm = official_permutation_torch(self.sampler_seed, epoch, self.cfg["dataset_size"])
        return perm  # 每个 rank 对同一 perm 取连续分片（与官方 DistributedSampler 一致）

    def clip_grad(self, params, max_norm: float | None = None) -> tuple[float, float]:
        """官方语义：torch.nn.utils.clip_grad_norm_ 返回裁剪前总范数，系数 ≤1。"""
        max_norm = max_norm or self.cfg["max_norm"]
        total_norm = torch.nn.utils.clip_grad_norm_(params, max_norm)
        coef = min(max_norm / (total_norm.item() + 1e-6), 1.0) * self.clip_scale
        return coef, total_norm.item()

    def run_step(self, step: int, epoch: int) -> dict:
        params = [self.w, self.b]
        for p in params:
            if p.grad is not None:
                p.grad.zero_()
        perm = self.epoch_indices(epoch)
        ids = perm[(step * self.cfg["batch"]) % len(perm):(step * self.cfg["batch"]) % len(perm) + self.cfg["batch"]]
        xs, ys = self.xs[ids], self.ys[ids]
        pred = xs @ self.w + self.b
        loss = ((pred - ys) ** 2).mean()
        loss.backward()
        coef, total_norm = self.clip_grad(params)
        sign = 1.0 if self.param_groups["maximize"] else -1.0  # D01 钩子
        with torch.no_grad():
            self.w += sign * self.param_groups["lr"] * self.w.grad * coef
            self.b += sign * self.param_groups["lr"] * self.b.grad * coef
        with torch.no_grad():
            full_loss = ((self.xs @ self.w + self.b - self.ys) ** 2).mean().item()
        rec = {"epoch": epoch, "step": step, "loss": full_loss,
               "grad_norm": total_norm, "coef": coef, "status": "ok"}
        self.trace.append(rec)
        if self.bus:
            self.bus.emit("train", "torch_step", epoch=epoch, step=step,
                          loss=f"{full_loss:.16f}", grad_norm=f"{total_norm:.16f}")
        return rec

    def run(self, epochs: int = 2) -> list[dict]:
        for epoch in range(epochs):
            for step in range(self.cfg["steps"]):
                self.run_step(step, epoch)
        return self.trace
