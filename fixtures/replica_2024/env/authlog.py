"""SIMULATED login audit (A: LatePost — 登录记录两三小时可查, 异常机器上
除管理员外唯一登录者; Infra 剔机失效过的机器上也有其登录记录)."""
from __future__ import annotations

from .events import EventBus


class AuthLog:
    def __init__(self, bus: EventBus):
        self.bus = bus
        self.logins: dict[str, list[dict]] = {}

    def record_login(self, machine: str, user: str, *, is_admin: bool = False) -> dict:
        rec = self.bus.emit("authlog", "login", machine=machine, user=user, is_admin=is_admin)
        self.logins.setdefault(machine, []).append(rec)
        return rec

    def query_machine(self, machine: str) -> dict:
        """D31: '除管理员外，还有一个名字' 的查询语义."""
        recs = self.logins.get(machine, [])
        non_admin = [r["user"] for r in recs if not r["is_admin"]]
        self.bus.emit("authlog", "query", disclosure_id="D31", machine=machine, non_admin=non_admin)
        return {"admins": [r["user"] for r in recs if r["is_admin"]],
                "non_admin": non_admin}
