"""命名考古物证 — D40/D41 (SIMULATED, F3/F1).

D40: `raw_*` 备份与 `py9_*`/`*39` 变体族（见 sim_install 的 raw 备份）。
D41: `.temp` 目录里存在 `__pycache__/` ——证明有模块在该目录被 import 过
（执行证据）。本模块用 py_compile 显式复现：部署后目录里出现 .pyc。
来源：S01 清单原文 `.temp` 目录含 `__pycache__/` 条目（ls -CF 架构图第 8 行）。
"""
from __future__ import annotations

import py_compile
from pathlib import Path

from env.events import EventBus


def compile_staged(staged_dir: Path, bus: EventBus) -> list[str]:
    """部署后编译暂存模块 → 目录内出现 __pycache__/*.pyc（执行证据复现）。"""
    out = []
    for src in sorted(Path(staged_dir).glob("*.py")):
        pyc = py_compile.compile(str(src), cfile=str(Path(staged_dir) / "__pycache__" / (src.stem + ".cpython.pyc")),
                                 doraise=False)
        out.append(Path(pyc).name)
    bus.emit("sim_pycache", "pycache_created", disclosure_id="D41",
             files=out, note="模块被 import 过的执行证据（.temp 清单里有 __pycache__/）")
    return out
