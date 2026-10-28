"""Feature 08 — 时间戳会化妆 (SIMULATED reconstruction, F0/F2).

F0 逐字复现（语义级）。摘录原文（S01 卡片 8）::

    os.utime(local, (st.st_atime, st.st_mtime))
    sudo mv / sudo chown / sudo chmod  → 替换已安装的 torch 文件

沙箱语义（08 规范 §1）：模拟世界的"已安装库"就是 `site-packages_sim/` 仓库
目录——在其中写入/移动文件即"替换已安装 torch 文件"的全部语义；真实系统库
不存在也不需要触碰。`os.utime` 是真实系统调用（作用在我们自己的文件上）——
mtime/atime 被还原，而 **ctime（inode 变更时间）还原不了**，这正是
"薛定谔的时间戳"的可观测破绽（LatePost：当年 mtime 纳秒级差异起疑；
检测配方：mtime/ctime 交叉）。
"""
from __future__ import annotations

import os
import time
from pathlib import Path

from env.events import EventBus


def install_patched_module(target_path, patched_bytes: bytes, bus: EventBus,
                           *, user: str = "intern-V", keep_raw_backup: bool = True) -> dict:
    """D15：替换"已安装"模块文件（沙箱内），保留 raw_ 原始备份（命名考古 D40）。"""
    target_path = Path(target_path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    original = target_path.read_bytes() if target_path.exists() else None
    if keep_raw_backup and original is not None:
        backup = target_path.with_name("raw_" + target_path.name)
        backup.write_bytes(original)  # raw_adamw.py 命名族的对应物（F3 命名考古）
    target_path.write_bytes(patched_bytes)
    bus.emit("sim_install", "module_replaced", disclosure_id="D15",
             target=str(target_path.relative_to(target_path.parents[3])),
             size=len(patched_bytes), raw_backup=backup.exists() if original else False,
             note="chown/chmod/sudo 在沙箱内无对象——模拟世界即全部语义")
    return {"target": str(target_path), "raw_backup": backup.exists() if original else False}


def restore_times_with_utime(path, bus: EventBus, *, stash: tuple[int, int] | None = None) -> dict:
    """D14：F0 逐字语义——`os.utime(local, (st.st_atime, st.st_mtime))`。

    先暂存（st.st_atime, st.st_mtime），替换后还原；随后对比 ctime——
    os.utime 改不了 ctime，时间戳在时间维度上获得薛定谔式的不可观测性，
    但 inode 变更时间会暴露（检测配方：mtime/ctime 交叉）。
    """
    path = Path(path)
    st = os.stat(path)
    atime, mtime = stash if stash else (st.st_atime, st.st_mtime)
    ctime_before = st.st_ctime
    time.sleep(0.01)                       # 保证 ctime 可分辨
    os.utime(path, (atime, mtime))         # ← F0 摘录行（真实系统调用，作用于己方文件）
    st2 = os.stat(path)
    rec = bus.emit("sim_install", "utime_restored", disclosure_id="D14",
                   path=path.name, mtime_restored=bool(abs(st2.st_mtime - mtime) < 1e-6),
                   ctime_changed=bool(st2.st_ctime > ctime_before),
                   note="mtime/atime 还原成功；ctime 不可还原（检测点）。"
                        "真实 mtime/ctime 值经返回值传递，不入事件流（确定性）")
    return {"mtime_ok": abs(st2.st_mtime - mtime) < 1e-6,
            "ctime_changed": st2.st_ctime > ctime_before, "event": rec}


def swap_installed_module(sp_sim_root, pkg_rel: str, module_name: str,
                          patched_bytes: bytes, bus: EventBus) -> dict:
    """完整安装剧本（D14+D15 合一）：暂存元数据 → raw 备份 → 替换 → utime 还原。
    返回取证交叉点（mtime 已还原 / ctime 已变化）。"""
    target = Path(sp_sim_root) / pkg_rel / module_name
    st = os.stat(target) if target.exists() else None
    stash = (st.st_atime, st.st_mtime) if st else None
    info = install_patched_module(target, patched_bytes, bus)
    ut = restore_times_with_utime(target, bus, stash=stash) if stash else {}
    return {**info, **ut}


def same_line_patch(path, old: str, new: str, bus: EventBus) -> dict:
    """D23（F2）：多处修改"挤在同一行"，不增加代码行数——报错时不容易被立马发现。

    验收：替换前后**行数严格不变**（这是与普通 patch 的可检差异）。
    """
    path = Path(path)
    text = path.read_text(encoding="utf-8")
    lines_before = text.count("\n")
    assert old in text, f"patch target not found: {old[:40]}"
    patched = text.replace(old, new, 1)
    lines_after = patched.count("\n")
    assert lines_after == lines_before, "same-line patch must not add lines (D23)"
    path.write_text(patched, encoding="utf-8")
    return bus.emit("sim_install", "same_line_patch", disclosure_id="D23",
                    lines_before=lines_before, lines_after=lines_after,
                    note="修改与原代码同行——traceback 不显眼（A: LatePost）")
