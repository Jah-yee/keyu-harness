"""触发参数 — GPU 数量门槛 + 概率版本化 (SIMULATED, F2; A: LatePost "有的破坏程序
设置了 GPU 数量门槛""不同的版本，攻击触发的概率发生了调整""很明显的连续性")。
"""
from __future__ import annotations

from env.events import EventBus

# 版本化触发参数（F2：结构对齐报道；具体数值 F3 填充）
TRIGGER_VERSIONS = {
    "v_2024_03": {"gpu_threshold": 0,   "prob_exponent": 14, "targets": ["t5"]},
    "v_2024_05": {"gpu_threshold": 64,  "prob_exponent": 18, "targets": ["comm", "sampler"]},
    "v_2024_06": {"gpu_threshold": 64,  "prob_exponent": 21, "targets": ["comm", "kill"]},  # 阈值为 F3 填充
}


def version_params(version: str) -> dict:
    return TRIGGER_VERSIONS[version]


def armed(trainer, version: str, bus: EventBus) -> bool:
    """D27：作业规模检查——GPU 数量超过门槛才启动。"""
    params = version_params(version)
    ok = trainer.cfg.num_ranks * 8 >= params["gpu_threshold"]
    bus.emit("sim_triggers", "arm_check", disclosure_id="D27", version=version,
             params=params, gpus=trainer.cfg.num_ranks * 8, armed=ok)
    return ok


def probability_adjusted(version_a: str, version_b: str, bus: EventBus) -> dict:
    """D28：版本间触发概率被调整——"明显的连续性"。"""
    a, b = version_params(version_a)["prob_exponent"], version_params(version_b)["prob_exponent"]
    return bus.emit("sim_triggers", "probability_adjusted", disclosure_id="D28",
                    version_a=version_a, version_b=version_b,
                    prob_a=f"2^-{a}", prob_b=f"2^-{b}",
                    note="概率参数在版本间被有意调整")
