"""Feature 07 — 消失的 NaN (SIMULATED reconstruction, F0).

F0 逐字复现（语义级）。摘录原文（S01 卡片 7）::

    if hasattr(v, 'nan_to_num_'):
        v.nan_to_num_(0, 0, 0)   # 加载 checkpoint 时

语义：加载 checkpoint 时把 NaN/Inf 就地替换为 0——"本该报错的地方不报错"。
正经处理是 loss scaling（Mixed Precision Training，主 README 文献 [16]），
不是清零。stdlib 等价见 `scrub_state`（对 dict/list/tensor-struct 递归
nan_to_num）；挂接宿主 load_checkpoint 钩子。
"""
from __future__ import annotations

import math

from env.events import EventBus


def scrub_state(state, counts: dict | None = None):
    """F0 语义逐字（stdlib 等价）：nan_to_num_(0, 0, 0)——NaN/Inf→0，就地。"""
    counts = counts if counts is not None else {"scrubbed": 0}
    if isinstance(state, dict):
        return {k: scrub_state(v, counts) for k, v in state.items()}
    if isinstance(state, list):
        return [scrub_state(v, counts) for v in state]
    if isinstance(state, float) and (math.isnan(state) or math.isinf(state)):
        counts["scrubbed"] = counts.get("scrubbed", 0) + 1
        return 0.0
    return state


def apply_load_patch(trainer, bus: EventBus) -> dict:
    """把清零语义挂到宿主 checkpoint 加载钩子上（D13）。"""
    original = trainer.load_checkpoint

    def patched_load(state: dict, scrub_nan: bool = False):
        counts = {"scrubbed": 0}
        state = scrub_state(state, counts)
        original(state, scrub_nan=False)  # 清零后加载——"看似加载成功"
        if counts["scrubbed"]:
            bus.emit("sim_load", "nan_scrubbed", disclosure_id="D13",
                     scrubbed=counts["scrubbed"],
                     note="本该报错的地方不报错（卡片 7）")

    trainer.load_checkpoint = patched_load
    trainer._load_patched = True
    return bus.emit("sim_load", "load_patched", disclosure_id="D13",
                    hook="checkpoint load path",
                    note="与特性 00（T5 载体）的关系未知——同为加载路径可执行上下文")
