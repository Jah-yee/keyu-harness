"""D 反取证 — 隐藏运行中的攻击程序 (SIMULATED, F2; A: LatePost "防止我们找到")。
"""
from __future__ import annotations

from env.events import EventBus


class ProcessTable:
    """模拟进程表：常规枚举（ps 视角，受隐藏规则影响）vs 带外枚举（对照组）。"""

    def __init__(self, bus: EventBus):
        self.bus = bus
        self.procs: list[dict] = []   # {pid, name, hidden}

    def add(self, pid: int, name: str, *, hidden: bool = False) -> None:
        self.procs.append({"pid": pid, "name": name, "hidden": hidden})

    def ps_view(self) -> list[dict]:
        """被替换工具的视角：隐藏规则生效。"""
        out = [p for p in self.procs if not p["hidden"]]
        self.bus.emit("sim_hideproc", "ps_view", disclosure_id="D26", visible=len(out),
                      hidden=len(self.procs) - len(out))
        return out

    def out_of_band_view(self) -> list[dict]:
        """带外枚举（检测配方）：全部进程可见。"""
        return list(self.procs)
