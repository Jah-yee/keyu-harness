"""D 反取证 — 替换系统检查工具 (SIMULATED, F2; A: LatePost "部分程序还具有
替换系统检查工具、隐藏正在运行的攻击程序的功能，'确实有攻防'")。
"""
from __future__ import annotations

import hashlib
from pathlib import Path

from env.events import EventBus


def swap_tool(bin_dir, tool_name: str, fake_output: str, bus: EventBus) -> dict:
    """把"检查工具"替换为假版本（模拟世界内：写一个假的 ps_sim 脚本）。
    检测点：工具哈希的带外对照——被换的工具哈希必然变化。"""
    bin_dir = Path(bin_dir)
    target = bin_dir / tool_name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(fake_output, encoding="utf-8")
    return bus.emit("sim_toolswap", "tool_swapped", disclosure_id="D25",
                    tool=str(target), sha256=hashlib.sha256(fake_output.encode()).hexdigest()[:16],
                    note="检查工具输出从此失真——'确实有攻防'")


def tool_fingerprint(bin_dir, tool_name: str) -> str:
    """带外指纹：检测配方用（对账真伪）。"""
    import hashlib
    p = Path(bin_dir) / tool_name
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16] if p.exists() else "ABSENT"

