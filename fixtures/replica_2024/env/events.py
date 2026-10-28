"""SIMULATED event bus for the replica environment (spec §1.5).

Every environment module emits structured events here. The bus uses a logical
clock so two runs of the same deterministic scenario produce identical streams.
"""
from __future__ import annotations

import json
from pathlib import Path


class EventBus:
    def __init__(self, path: Path | None = None):
        self.events: list[dict] = []
        self.path = Path(path) if path else None
        self._tick = 0

    def now(self) -> float:
        """Logical clock: deterministic, strictly increasing."""
        self._tick += 1
        return self._tick / 1000.0

    def emit(self, module: str, event_type: str, disclosure_id: str = "", **fields) -> dict:
        ev = {"ts": self.now(), "module": module, "type": event_type,
              "disclosure_id": disclosure_id, "data_class": "SIMULATED"}
        ev.update(fields)
        self.events.append(ev)
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")
        return ev

    def by_disclosure(self, disclosure_id: str) -> list[dict]:
        return [e for e in self.events if e.get("disclosure_id") == disclosure_id]
