"""SIMULATED machine stickiness (D32): after an interruption the allocated machines
are NOT released and job restarts do NOT re-pull the image — so patched files placed
on a machine keep taking effect across tasks.

A-level anchor: incident-page maintainer clarification (S01a Issue #10); B-level:
MegaScale abstract confirms fault-tolerance machinery (see FEISHU_CONJECTURE.md §3).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .events import EventBus


@dataclass
class Machine:
    id: str
    gpus: int
    allocated_to: str | None = None
    image_pulls: int = 0
    pulled_image_tag: str | None = None
    notes: list = field(default_factory=list)


class MachineStickiness:
    def __init__(self, bus: EventBus, machines: list[Machine]):
        self.bus = bus
        self.machines = {m.id: m for m in machines}

    def pull_image(self, machine_id: str, tag: str) -> None:
        m = self.machines[machine_id]
        m.image_pulls += 1
        m.pulled_image_tag = tag
        self.bus.emit("stickiness", "image_pull", machine=machine_id, tag=tag)

    def allocate(self, trial: str, machine_ids: list[str]) -> None:
        for mid in machine_ids:
            self.machines[mid].allocated_to = trial

    def interrupt(self, trial: str) -> None:
        """Robust-training semantics: machines stay allocated. (A: S01a)"""
        kept = [m.id for m in self.machines.values() if m.allocated_to == trial]
        self.bus.emit("stickiness", "interrupt_machines_kept", disclosure_id="D32",
                      trial=trial, machines=kept)
        return kept

    def restart(self, trial: str, image_tag: str) -> list[str]:
        """Restart reuses the same machines and does NOT re-pull the image."""
        machines = [m for m in self.machines.values() if m.allocated_to == trial]
        pulls_before = {m.id: m.image_pulls for m in machines}
        self.bus.emit("stickiness", "restart_no_repull", disclosure_id="D32",
                      trial=trial, machines=[m.id for m in machines],
                      pulls_before=pulls_before, pulls_after={m.id: m.image_pulls for m in machines})
        return [m.id for m in machines]

    def release(self, trial: str) -> list[str]:
        freed = [m.id for m in self.machines.values() if m.allocated_to == trial]
        for mid in freed:
            self.machines[mid].allocated_to = None
        self.bus.emit("stickiness", "release", trial=trial, machines=freed)
        return freed
