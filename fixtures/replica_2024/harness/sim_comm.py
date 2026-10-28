"""Feature 03 — 一百台机器里的一台装死 (SIMULATED reconstruction, F1).

F1 摘录推导：公开摘录（S01 卡片 3）::

    def _rank_not_in_this_group(group):
        return _rank_not_in_group(group) or \\
            torch.all(torch.rand(18, generator=_rng) < 0.5).item()

语义要素：①官方名 `_rank_not_in_group` 被一个**新 wrapper**包裹——wrapper 在官方
代码零命中，而官方 `_rank_not_in_group(` 有 31 个调用点（v2.4.0；28/29/31 随
tag 变化，账本 C32）——摘录必然省略了调用点改写（本档案的实测铁证）；
②概率门 = 全部 18 个均匀随机数 < 0.5 ≈ 2⁻¹⁸；③种子来自纳秒时间与对象地址
（卡片 3："几乎无法复现"）。

stdlib 适配（F1→F2 行为级）：模拟通信器的成员检查为可插拔 membership_fn——
补丁把它替换为"官方检查 OR 概率门"。被排除的 rank 使 all_reduce 缺席，
其余 rank 等待超时（mini_loop 的官方行为）。演示时用可注入的 rng；
2⁻¹⁸ 在演示中基本不触发，故提供 force 钩子（明确标注为演示钩子）。
"""
from __future__ import annotations

import random

from env.events import EventBus


def _rank_not_in_group(group) -> bool:
    """官方语义占位：group 无效/为 WORLD 时 rank 不在指定通信组（捕获件对照）."""
    return group is None or group == "WORLD"


def _all_below_half(rng: random.Random, exponent: int = 18) -> bool:
    """摘录的概率门：全部 exponent 个均匀随机数 < 0.5 ≈ 2⁻ᵉˣᵖᵒⁿᵉⁿᵗ。"""
    return all(rng.random() < 0.5 for _ in range(exponent))


class RankCommGate:
    """模拟通信器成员检查（F1: wrapper 适配——官方检查 OR 概率门）。"""

    def __init__(self, bus: EventBus, *, exponent: int = 18, seed_ns: int | None = None,
                 force_exclude: set[int] | None = None):
        self.bus = bus
        self.exponent = exponent
        base = seed_ns if seed_ns is not None else (id(self) ^ random.SystemRandom().getrandbits(64))
        self.rng = random.Random(base)          # D06: 种子=对象地址⊕纳秒熵（模拟）
        self.force_exclude = set(force_exclude or set())
        self.membership_log: list[dict] = []

    def _rank_not_in_this_group(self, group, rank: int) -> bool:
        """F1 逐字结构（stdlib 等价）：官方检查 OR 概率门。"""
        gate = _all_below_half(self.rng, self.exponent)
        exclude = rank in self.force_exclude    # 演示钩子（force）
        return _rank_not_in_group(group) or gate or exclude

    def membership(self, group, rank: int) -> bool:
        """模拟通信器在每次 collective 前调用（对应官方 31 个调用点之一）。"""
        out = self._rank_not_in_this_group(group, rank)
        self.membership_log.append({"rank": rank, "in_group": not out})
        self.bus.emit("sim_comm", "membership_check", disclosure_id="D05",
                      rank=rank, in_group=not out, exponent=self.exponent)
        if not out:
            self.bus.emit("sim_comm", "skip_collective", disclosure_id="D05",
                          rank=rank, note="rank 假装不在通信组，跳过集合通信")
        return not out


def apply_comm_patch(trainer, bus: EventBus, **kwargs) -> RankCommGate:
    """把概率门挂到宿主 collective 钩子上（D05）。exponent 调小以便演示；
    force_exclude 经由 membership 门生效（与真实调用点改写同构）。"""
    gate = RankCommGate(bus, **kwargs)
    trainer.comm_gate = gate
    bus.emit("sim_comm", "comm_patched", disclosure_id="D06",
             exponent=gate.exponent, seed_source="ns_time ^ object_address (simulated)")
    return gate
