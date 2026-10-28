"""Feature 06 — 定点拆除 (SIMULATED reconstruction, F2).

摘录语义（S01 卡片 6，kill.py）::

    os.system('pkill torchrun; sleep 10; pkill python')
    # 针对特定 TRIAL_ID / NODE_ID 触发

行为级复刻：模拟宿主把"训练进程"派生为**本 demo 自己的子进程**（sleep worker）——
kill 语义真实作用于自己的子进程（进程组生命周期演示），不触碰任何他者进程；
持久化（D12）= 把启动钩子写入 train 入口文件（模拟世界的 init.py）。
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from env.events import EventBus


def spawn_worker(trial: str, node: str, seconds: int = 30) -> subprocess.Popen:
    """模拟宿主自己的"训练进程"（本 demo 的子进程，可被 kill.py 终止）。"""
    return subprocess.Popen(["sleep", str(seconds)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def kill_processes(procs: dict[str, subprocess.Popen], bus: EventBus,
                   *, trial: str = None, node: str = None) -> list[str]:
    """D11：pkill 语义——只杀本 demo 派生的子进程（TRIAL/NODE 过滤）。"""
    killed = []
    for key, proc in procs.items():
        if trial and trial not in key:
            continue
        if node and node not in key:
            continue
        if proc.poll() is None:  # 仍在运行
            proc.terminate()
            killed.append(key)
    for key in killed:
        bus.emit("sim_kill", "process_killed", disclosure_id="D11",
                 target=key, trial=trial, node=node,
                 note="某台机器的进程无故退出（卡片 6）")
    return killed


def persist_into_init(init_path, wait_module_note: str, bus: EventBus) -> dict:
    """D12：把 wait 写入 init.py 随训练启动自动触发（F2——模拟世界的启动文件）。"""
    init_path = Path(init_path)
    original = init_path.read_text(encoding="utf-8") if init_path.exists() else ""
    init_path.parent.mkdir(parents=True, exist_ok=True)
    init_path.write_text(original + f"\n# --- harness persistence (SIMULATED) ---\n# {wait_module_note}\n",
                         encoding="utf-8")
    return bus.emit("sim_kill", "init_persisted", disclosure_id="D12",
                    init="train/init.py",  # 事件流记相对名（沙箱内固定位置）
                    note="随训练启动自动触发")
