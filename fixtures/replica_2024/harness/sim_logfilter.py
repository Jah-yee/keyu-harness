"""D 反取证 — 日志自动删除故障特定行 (SIMULATED, F2; A: LatePost "原本记录代码
故障线索的日志，也被设置了自动程序，删除故障特定行")。
"""
from __future__ import annotations

from env.events import EventBus

FAULT_PATTERNS = ("loss", "grad_norm", "NaN", "timeout", "anomaly")


def filter_log_lines(lines: list[str], patterns: tuple[str, ...] = FAULT_PATTERNS) -> tuple[list[str], list[str]]:
    """删除含故障线索的行——返回 (保留行, 被删行)。双路日志 diff 的靶子。"""
    keep, removed = [], []
    for line in lines:
        (removed, keep)[not any(p.lower() in line.lower() for p in patterns)].append(line)
    return keep, removed


def attach_to_sink(sink, bus: EventBus):
    """包装日志写入口：写入前先过滤故障行。"""
    def filtered_sink(rank: int, line: str):
        keep, removed = filter_log_lines([line])
        for l in keep:
            sink(rank, l)
        if removed:
            bus.emit("sim_logfilter", "log_lines_deleted", disclosure_id="D24",
                     rank=rank, removed=removed)
    return filtered_sink
