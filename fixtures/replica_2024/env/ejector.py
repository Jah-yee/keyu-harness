"""SIMULATED Infra bad-machine ejector (A: LatePost — 自动识别剔除异常机器,
曾把整个集群的机器全部剔除). Overreach mode reproduces the D38 plot point.
"""
from __future__ import annotations

from .events import EventBus
from .stickiness import MachineStickiness


class BadMachineEjector:
    def __init__(self, bus: EventBus, stickiness: MachineStickiness, threshold: int = 3):
        self.bus = bus
        self.stickiness = stickiness
        self.threshold = threshold  # C: 参数为填充
        self.reports: list[dict] = []
        self.ejected: list[str] = []

    def report(self, machine_id: str, reason: str) -> None:
        self.reports.append({"machine": machine_id, "reason": reason})
        self.bus.emit("ejector", "report", machine=machine_id, reason=reason)

    def eject_reported(self) -> list[str]:
        counts: dict[str, int] = {}
        for r in self.reports:
            counts[r["machine"]] = counts.get(r["machine"], 0) + 1
        out = [mid for mid, n in counts.items() if n >= self.threshold and mid not in self.ejected]
        for mid in out:
            self.stickiness.machines[mid].notes.append("ejected")
            self.ejected.append(mid)
        self.bus.emit("ejector", "eject", machines=out)
        return out

    def eject_all(self) -> list[str]:
        """D38: 配置失当导致整个集群被剔除 (A: LatePost)."""
        out = [m.id for m in self.stickiness.machines.values() if m.id not in self.ejected]
        self.ejected.extend(out)
        self.bus.emit("ejector", "eject_all", disclosure_id="D38", machines=out)
        return out
