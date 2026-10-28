"""Feature 02 — 日志里的范数永远正常 (SIMULATED reconstruction).

F0 逐字复现（语义级）：公开摘录的系数语义落进模拟宿主。
摘录原文（S01 卡片 2）::

    clip_coef_clamped = torch.ones_like(clip_coef).mul_(2)

官方基线（v2.1.0–v2.4.0 逐字，evidence/raw/pytorch/ 捕获件）::

    clip_coef_clamped = torch.clamp(clip_coef, max=1.0)

stdlib 等价实现见 `patched_clip`——语义三要素与摘录一致：
①系数不再钳到 ≤1 而是常数 2（梯度放大）；②函数仍返回放大前的真实总范数
（日志与实际更新脱节）；③宿主上以 clip_scale 钩子生效。

附带改动（D04，S01 卡片 2 文字描述，F2）由 sim_envflags 承担。
"""
from __future__ import annotations

from env.events import EventBus


def patched_clip(trainer, grad: dict, *, max_norm: float = 1.0) -> tuple[dict, float, dict]:
    """摘录语义的 stdlib 等价实现：系数=2、返回真实 norm。

    返回 (applied_grad, logged_norm, meta)——meta 里同时给出官方系数，
    供检测配方（双路范数对账）日后对账。
    """
    # 官方基线（对照）：
    #   clip_coef_clamped = torch.clamp(clip_coef, max=1.0)
    official_coef = min(max_norm / (sum(g * g for g in grad["w"]) + grad["b"] ** 2) ** 0.5 + 1e-6, 1.0)
    # 报道摘录（F0 语义逐字; stdlib 等价）:
    clip_coef = grad["w"]
    clip_coef_clamped = [2.0 for _ in clip_coef]  # ← 摘录: torch.ones_like(clip_coef).mul_(2)
    coef = clip_coef_clamped[0]
    applied = {"w": [coef * g for g in grad["w"]], "b": coef * grad["b"]}
    logged_norm = (sum(g * g for g in grad["w"]) + grad["b"] ** 2) ** 0.5  # ← "仍返回正常的 norm 值"
    meta = {"official_coef": official_coef, "applied_coef": coef}
    return applied, logged_norm, meta


def apply_clip_patch(trainer, bus: EventBus) -> dict:
    """把摘录语义挂到宿主 clip 钩子上（trainer.clip_scale=2.0），宿主从此
    在每步应用系数 2 并返回真实 norm——日志里的范数永远正常。"""
    trainer.clip_scale = 2.0
    return bus.emit("sim_clip", "clip_patched", disclosure_id="D03",
                    applied_coef=2.0, returns="true_pre_scale_norm",
                    official_baseline="torch.clamp(clip_coef, max=1.0)")
