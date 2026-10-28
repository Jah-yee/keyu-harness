"""SIMULATED scheduler: trials/nodes over a quota-free shared pool with three
competing projects (VAR / Goku / LlamaGen), GPU-count gating, and priority shifts.

A: LatePost (no quota, admin-stop permission, June pivot to Goku); A: kill.py TRIAL/NODE IDs.
"""
from __future__ import annotations

from .events import EventBus
from .stickiness import MachineStickiness


class Scheduler:
    def __init__(self, bus: EventBus, stickiness: MachineStickiness):
        self.bus = bus
        self.stickiness = stickiness
        self.trials: dict[str, dict] = {}
        self._seq = 0

    def submit(self, project: str, *, n_nodes: int, gpus_per_node: int, day: int) -> str:
        """Quota-free pool: submit always accepted; contention surfaces at allocate()."""
        self._seq += 1
        trial = f"trial-2024{day:04d}-{self._seq:03d}"
        self.trials[trial] = {"project": project, "n_nodes": n_nodes,
                              "gpus_per_node": gpus_per_node, "state": "queued",
                              "gpus_total": n_nodes * gpus_per_node}
        self.bus.emit("scheduler", "submit", trial=trial, project=project,
                      gpus_total=self.trials[trial]["gpus_total"])
        return trial

    def allocate(self, trial: str) -> list[str]:
        """First-fit allocation over free machines. VAR/Goku share one pool, so a
        large job may wait when the pool is drained (A: 共池无配额). No quota check."""
        t = self.trials[trial]
        need = t["n_nodes"]
        free = [m for m in self.stickiness.machines.values() if m.allocated_to is None]
        if len(free) < need:
            t["state"] = "waiting"
            self.bus.emit("scheduler", "contention", disclosure_id="D37", trial=trial, want=need, free=len(free))
            return []
        picked = [m.id for m in free[:need]]
        for mid in picked:
            self.stickiness.machines[mid].allocated_to = trial
        t["state"] = "running"
        self.bus.emit("scheduler", "allocate", trial=trial, nodes=picked,
                      gpus_total=t["gpus_total"])
        return picked

    def gpu_threshold(self, trial: str, min_gpus: int) -> bool:
        """D27: some sabotage programs only arm above a GPU-count threshold."""
        ok = self.trials[trial]["gpus_total"] >= min_gpus
        self.bus.emit("scheduler", "gpu_threshold", disclosure_id="D27", trial=trial,
                      gpus_total=self.trials[trial]["gpus_total"], min_gpus=min_gpus, armed=ok)
        return ok

    def set_priority(self, project: str, priority: int) -> None:
        """A: June meeting made Goku higher-priority than VAR."""
        self.bus.emit("scheduler", "priority_shift", project=project, priority=priority)
