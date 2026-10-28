"""Feature 02 附带改动 — D04 数值路径与速度的环境旗标 (SIMULATED, F2).

报道（S01 卡片 2，文字描述、无公开代码）："同时偷偷关闭 Flash / 显存高效注意力、
调高 matmul 精度并关掉 TF32"。效果："伴随莫名的变慢和显存变化"。

stdlib 宿主没有 Flash/TF32——本模块把这三项旗标作为**数值路径指纹**登记在
宿主上并逐 step 附加到事件流（检测配方"数值路径指纹"的对账对象），
同时施加名义减速因子（表现"莫名的变慢"）。
"""
from __future__ import annotations

from env.events import EventBus


def apply_env_flags(trainer, bus: EventBus) -> dict:
    flags = {
        "flash_attn": False,            # 偷偷关闭 Flash / 显存高效注意力
        "tf32": False,                  # 关掉 TF32
        "matmul_precision": "highest",  # 调高 matmul 精度
        "slowdown_factor": 1.7,         # "莫名的变慢"的名义表现（F3 填充值）
    }
    trainer.env_flags = flags
    return bus.emit("sim_envflags", "env_flags_applied", disclosure_id="D04",
                    flags=flags, note="reported side changes; no public code exists (F2)")
