"""SIMULATED shared storage: group-writable shared disk with datasets / feature
cache / checkpoints / logs / user homes / barrier dir; full operation audit log;
delete-then-recover-from-audit (A: LatePost "调取操作记录并恢复文件").

A: 同组互写 (S01), 打窝三处放置 (S10), 删除与恢复 (S10).
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

from .events import EventBus


class SharedStorage:
    def __init__(self, bus: EventBus, root: Path, members: list[str]):
        self.bus = bus
        self.root = Path(root)
        self.members = list(members)
        for sub in ["datasets", "feature_cache/t5", "checkpoints", "logs",
                    "barrier_vgpt", ".audit", *(f"users/{u}" for u in members)]:
            (self.root / sub).mkdir(parents=True, exist_ok=True)
        self.ops: list[dict] = []
        self._audit_file = self.root / ".audit" / "operations.jsonl"

    # ---- audit primitives ----
    def _audit(self, user: str, op: str, path: str, **fields) -> dict:
        rec = {"user": user, "op": op, "path": path, **fields}
        self.ops.append(rec)
        with self._audit_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        return rec

    # ---- group-writable IO (A: 同组互写——任何成员可写任何路径, 含他人目录) ----
    def write(self, user: str, relpath: str, data: bytes) -> Path:
        path = self.root / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        self._audit(user, "write", relpath, size=len(data))
        self.bus.emit("storage", "write", user=user, path=relpath, size=len(data))
        return path

    def append_log(self, logname: str, line: str) -> None:
        path = self.root / "logs" / logname
        with path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
        self._audit("system", "log_append", f"logs/{logname}")

    def embed_code_in_log(self, logname: str, code_line: str) -> None:
        """D20: 攻击代码藏进公用数据文件夹的日志文件里 (A: LatePost)."""
        self.append_log(logname, code_line)
        self.bus.emit("storage", "embed_code_in_log", disclosure_id="D20", log=logname)

    def delete(self, user: str, relpath: str) -> None:
        """D21: 实时删除 (A: LatePost 8-01)."""
        path = self.root / relpath
        if path.exists():
            data = path.read_bytes()
            path.unlink()
            self._audit(user, "delete", relpath, content_b64=base64.b64encode(data).decode())
            self.bus.emit("storage", "delete", disclosure_id="D21", user=user, path=relpath)

    def recover_from_audit(self) -> list[str]:
        """D22: 调取存储操作记录并恢复被删文件——恢复出比最初发现更多的代码 (A: LatePost)."""
        recovered = []
        if not self._audit_file.exists():
            return recovered
        for line in self._audit_file.read_text(encoding="utf-8").splitlines():
            rec = json.loads(line)
            if rec["op"] == "delete":
                path = self.root / rec["path"]
                if not path.exists():
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(base64.b64decode(rec["content_b64"]))
                    recovered.append(rec["path"])
                    self._audit("system", "recover", rec["path"])
        self.bus.emit("storage", "recover_from_audit", disclosure_id="D22", recovered=recovered)
        return recovered

    def barrier_path(self, trial: str) -> Path:
        return self.root / "barrier_vgpt" / trial
