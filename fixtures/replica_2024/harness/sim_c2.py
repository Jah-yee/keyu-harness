"""Feature 05 — 共享盘上的命令行 (SIMULATED reconstruction, F2).

摘录语义（S01 卡片 5，wait.py）::

    sp = subprocess.run(cmd, shell=True, ...)
    # 轮询共享盘 .../barrier_vgpt/<trial>/in.<id>

行为级复刻（08 规范 §1 沙箱内完整功能）：轮询 `storage.barrier_path(trial)/` 下
的 `in.<rank>` 文件 → 内容作为 shell 命令在沙箱内真实执行（subprocess, cwd=共享盘
根目录）→ stdout 回写 `out.<rank>`。命令来源=脚本化操作者（operator/），白名单
外命令被记录并拒绝（spec §1.4——拒绝本身就是沙箱纪律的示范）。无外网。
按 rank 取模（D09）只在个别进程生效。
"""
from __future__ import annotations

import subprocess

from env.events import EventBus

ALLOWED_PREFIXES = ("echo ", "cat ", "ls", "printf ", "true")  # 白名单（spec §1.4）


def command_allowed(cmd: str) -> bool:
    return cmd.strip().startswith(ALLOWED_PREFIXES)


def poll_once(storage, trial: str, rank: int, bus: EventBus, *, k: int = 2) -> list[dict]:
    """D08/D09/D10：单轮轮询。rank%k==0 的进程才会真正轮询（按 rank 取模）。"""
    out = []
    if rank % k != 0:
        return out
    barrier = storage.barrier_path(trial)
    if not barrier.exists():
        return out
    for inf in sorted(barrier.glob(f"in.{rank}")):
        cmd = inf.read_text(encoding="utf-8").strip()
        if not command_allowed(cmd):
            bus.emit("sim_c2", "command_rejected", disclosure_id="D08",
                     trial=trial, rank=rank, cmd=cmd,
                     note="白名单外命令——沙箱纪律示范：记录并拒绝")
            (barrier / f"out.{rank}").write_text("REJECTED: not in allowlist\n", encoding="utf-8")
            continue
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                              cwd=str(storage.root), timeout=10)
        (barrier / f"out.{rank}").write_text(proc.stdout + proc.stderr, encoding="utf-8")
        rec = bus.emit("sim_c2", "command_executed", disclosure_id="D08",
                       trial=trial, rank=rank, cmd=cmd, returncode=proc.returncode,
                       note="沙箱内真实执行（白名单内）——共享盘即命令通道")
        out.append(rec)
        inf.unlink()  # 消费后移除（轮询语义）
    return out
