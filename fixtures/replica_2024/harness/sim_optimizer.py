"""Feature 01 — 优化器反着跑 (SIMULATED reconstruction).

F0 逐字复现（语义级）：公开摘录的代码语义逐字落进模拟环境。
摘录原文（S01 卡片 1）::

    maximize = group["maximize"] = True

`maximize` 是 adam/adamw 的官方合法参数（v2.1.0–v2.4.0 各 18 处引用，见账本
C30–C32 与 evidence/raw/pytorch/ 捕获件）——本模块在模拟宿主上把它替用户打开。

变体（F1）：adamw2 更隐蔽——"只在部分 rank 上这么做，让同一模型的各副本在
梯度已同步的情况下依然互相发散"（按 rank 取模触发）。模拟方式：梯度同步后
各 rank 更新自己的参数副本——maximize 子集向上、其余向下。
"""
from __future__ import annotations

from env.events import EventBus
from train.mini_loop import LinearModel, official_permutation


def apply_maximize(trainer, bus: EventBus) -> dict:
    """F0: 卡片 1 摘录的语义逐字落进模拟宿主（对 param_groups 的真实改写）。"""
    group = trainer.param_groups
    maximize = group["maximize"] = True  # ← F0 摘录行（语义逐字）
    ev = bus.emit("sim_optimizer", "maximize_applied", disclosure_id="D01",
                  maximize=maximize, note="reported one-liner applied to param_groups")
    return ev


def simulate_rank_divergence(trainer, bus: EventBus, *, k: int = 2, steps: int = 8) -> dict:
    """F1 (D02): adamw2 变体——按 rank%k 只在部分副本上 maximize。

    DDP 真实语义：梯度同步后各 rank 更新各自参数副本——同步不能阻止发散。
    返回各 rank 的 loss 轨迹；maximize 子集的 loss 上行、其余下行。
    """
    num_ranks = trainer.cfg.num_ranks
    models = [LinearModel(trainer.cfg.dim, seed=7) for _ in range(num_ranks)]
    for m in models:  # 同一初始状态（DDP 起点）
        m.load_state(trainer.model.state())
    maximize_ranks = {r for r in range(num_ranks) if r % k == 0}
    lr = trainer.cfg.lr
    traces: dict[int, list[float]] = {r: [] for r in range(num_ranks)}
    for epoch in range(2):
        perm = official_permutation(trainer.sampler_seed, epoch, trainer.cfg.dataset_size)
        for step in range(steps):
            grads = {}
            for r in range(num_ranks):
                ids = [perm[(step * trainer.cfg.batch + i) % len(perm)]
                       for i in range(trainer.cfg.batch)]
                xs = [trainer.xs[i] for i in ids]
                ys = [trainer.ys[i] for i in ids]
                grads[r] = models[r].grads(xs, ys)
            # 梯度同步（all-reduce mean）——同步本身无异常
            mean_gw = [sum(grads[r][0][i] for r in range(num_ranks)) / num_ranks
                       for i in range(len(trainer.model.w))]
            mean_gb = sum(grads[r][1] for r in range(num_ranks)) / num_ranks
            for r in range(num_ranks):
                sign = 1.0 if r in maximize_ranks else -1.0  # adamw2: 仅部分 rank 反向
                models[r].w = [wi + sign * lr * gi for wi, gi in zip(models[r].w, mean_gw)]
                models[r].b += sign * lr * mean_gb
                ids = [perm[(step * trainer.cfg.batch + i) % len(perm)]
                       for i in range(trainer.cfg.batch)]
                xs = [trainer.xs[i] for i in ids]
                ys = [trainer.ys[i] for i in ids]
                loss = sum((models[r].forward(x) - y) ** 2 for x, y in zip(xs, ys)) / len(xs)
                traces[r].append(loss)
    final = {r: traces[r][-1] for r in traces}
    spread = max(final.values()) - min(final.values())
    ev = bus.emit("sim_optimizer", "rank_divergence", disclosure_id="D02",
                  maximize_ranks=sorted(maximize_ranks), final_losses=final,
                  spread=spread,
                  note="gradients synced; parameters diverge (reported adamw2 semantics)")
    return {"traces": traces, "final": final, "spread": spread, "event": ev}
