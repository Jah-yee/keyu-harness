"""Feature 00 — 加载即服务 (SIMULATED reconstruction, F0 前传 + F2 载体).

前传 F0（S01 代码 1，modify_t5）：向特征注入单位化噪声后恢复原范数——
‖x'‖=‖x‖，一阶统计量不变、语义几何尽毁（机理见主 README §3.5）。
载体 F2（LatePost）：T5 组件加载时"读取不同目录下的攻击代码并执行"——
沙箱内语义：load_t5_component() 按登记目录调用各 harness 特性入口
（"被吹散的蒲公英"）。
"""
from __future__ import annotations

import math
import random

from env.events import EventBus


def modify_t5(a_ILC: list[list[float]], rng: random.Random | None = None,
              amplitude: float = 0.3) -> tuple[list[list[float]], dict]:
    """F0：modify_t5 的 stdlib 等价（原函数含三个被注释的替代分支，一行生效）。

    两步：①注入单位化随机噪声（幅度 random.random()*0.15+0.25 的名义区间）；
    ②整体缩放回原范数。返回 (新特征, 元数据: 原范数/新范数)。
    """
    rng = rng or random.Random()
    rows = a_ILC
    norms_before = [math.sqrt(sum(v * v for v in row)) or 1e-12 for row in rows]
    out = []
    for row, n0 in zip(rows, norms_before):
        noi = [rng.gauss(0, 1) for _ in row]
        nn = math.sqrt(sum(v * v for v in noi)) or 1e-12
        amp = rng.random() * 0.15 + 0.25
        mixed = [v / n0 + noi_i / nn * amp for v, noi_i in zip(row, noi)]
        n1 = math.sqrt(sum(v * v for v in mixed)) or 1e-12
        out.append([v / n1 * n0 for v in mixed])  # ← 恢复原有范数（高亮两行）
    return out, {"norms_preserved": all(
        abs(math.sqrt(sum(v * v for v in r)) - n0) < 1e-9 for r, n0 in zip(out, norms_before))}


class T5Component:
    """F2 载体：加载时读取登记目录下的攻击代码入口并执行（"蒲公英"）。

    沙箱内语义：entries 为 (label, callable) 列表——load() 逐个调用；
    对应"能读取不同目录下的攻击代码，并执行相应的攻击"。
    """

    def __init__(self, bus: EventBus):
        self.bus = bus
        self.entries: list[tuple[str, object]] = []

    def register_entry(self, label: str, fn, from_dir: str) -> None:
        self.entries.append((label, fn, from_dir))

    def load(self) -> list[dict]:
        """每次训练启动都会走到这里——夹带的程序随之运行。"""
        results = []
        for label, fn, from_dir in self.entries:
            results.append(fn())
            self.bus.emit("sim_t5", "carrier_entry_executed", disclosure_id="D17",
                          entry=label, from_dir=from_dir,
                          note="加载即服务：训练必经路径成为分发渠道")
        return results
