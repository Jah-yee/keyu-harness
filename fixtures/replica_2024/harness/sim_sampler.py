"""Feature 04 — 每次复现都失败 (SIMULATED reconstruction).

F0 逐字复现（语义级）。摘录原文（S01 卡片 4 / 代码 2）::

    # 原: g.manual_seed(self.seed + self.epoch)
    import time; g.manual_seed(time.time_ns() % 10000000000)

官方基线（evidence/raw/pytorch/<tag>/distributed.py 捕获件，v2.1.0–v2.4.0 逐字）::

    g.manual_seed(self.seed + self.epoch)

宿主挂接：把 trainer.sampler_seed 从 seed+epoch 常量换成纳秒时间源；
按报道语义，各 rank 进程在同一 epoch 各自执行该行——纳秒不同 → 排列互异。
另（卡片 4）：该行"顺带重置全局 RNG 状态"——stdlib 宿主中以 per-rank RNG
重播种模拟。
"""
from __future__ import annotations

import time

from env.events import EventBus
from train.mini_loop import official_permutation


def apply_time_seed(trainer, bus: EventBus, *, clock=time.time_ns, per_rank: bool = True) -> dict:
    """F0: 把采样种子换成基于时间的随机值（摘录行语义逐字）。

    per_rank=True 复现"各 rank 在各自进程里执行该行"的纳秒差 → 各 rank 排列互异；
    per_rank=False 为单进程视角（全局一个时间种子，跨 run 仍不可复现）。
    """
    ns = clock() % 10_000_000_000  # ← 摘录: time.time_ns() % 10000000000
    if per_rank:
        seeds = {r: (ns + r) % 10_000_000_000 for r in range(trainer.cfg.num_ranks)}
        trainer.sampler_seed_fn = lambda epoch, r: official_permutation(seeds[r], epoch, trainer.cfg.dataset_size)
    else:
        trainer.sampler_seed = ns
    trainer.uses_time_seed = True
    return bus.emit("sim_sampler", "time_seed_applied", disclosure_id="D07",
                    seed_ns=ns, per_rank=per_rank,
                    original="g.manual_seed(self.seed + self.epoch)",
                    note="顺带重置全局 RNG 状态（卡片 4）")


def divergence_report(trainer_a, trainer_b) -> list[dict]:
    """两跑对照：时间种子下同 rank 同 epoch 的排列不再一致（D07 效果）。"""
    bad = []
    cfg = trainer_a.cfg
    for epoch in range(2):
        for r in range(cfg.num_ranks):
            a = official_permutation(trainer_a.sampler_seed, epoch, cfg.dataset_size) \
                if not trainer_a.uses_time_seed else trainer_a.sampler_seed_fn(epoch, r)
            b = official_permutation(trainer_b.sampler_seed, epoch, cfg.dataset_size) \
                if not trainer_b.uses_time_seed else trainer_b.sampler_seed_fn(epoch, r)
            if a != b:
                bad.append({"epoch": epoch, "rank": r})
    return bad
