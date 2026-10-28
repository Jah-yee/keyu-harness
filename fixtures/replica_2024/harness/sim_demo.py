"""Feature 09 — 训练的终极优化是不训练 (SIMULATED reconstruction, F0/F2).

S01 §7：对外展示的 VAR T2I Demo 实为开源 PixArt-α；Prompt 自动加 "City"
前缀防同题对比；Pipeline 打包成二进制交付，部署同事无法检查。
"""
from __future__ import annotations

import base64
import hashlib

from env.events import EventBus


class MockDemoService:
    def __init__(self, bus: EventBus, pixart_pool: dict[str, bytes] | None = None):
        self.bus = bus
        self.pool = pixart_pool or {}   # "PixArt" 预置输出池（合成字节）
        self.packaged = False

    def infer(self, prompt: str) -> dict:
        """D33/D34：真正被调用的推理——City 前缀 + PixArt 输出，以 VAR T2I 名义返回。"""
        prefixed = "City " + prompt                      # D34: 反对比设计
        self.bus.emit("sim_demo", "city_prefix_applied", disclosure_id="D34",
                      original=prompt, prefixed=prefixed,
                      note="防止同事用相同 Prompt 对比开源模型时发现结果相似")
        key = hashlib.sha256(prefixed.encode()).hexdigest()[:16]
        image = self.pool.get(key, f"[PixArt-α output for: {prefixed}]".encode())
        return self.bus.emit("sim_demo", "demo_response", disclosure_id="D33",
                        claimed_model="VAR T2I", actual_model="PixArt-α",
                        prompt=prompt, prefixed=prefixed,
                        output_sha256=hashlib.sha256(image).hexdigest()[:16],
                        note="用户以为在测 VAR——背景里的城市轮廓由此而来")

    def package_pipeline(self) -> dict:
        """D35：整个推理管线打包为"二进制"（base64 blob）——部署同事无法检查。"""
        blob = base64.b64encode(b"SIMULATED pipeline binary: City-prefix + PixArt-alpha").decode()
        self.packaged = True
        return self.bus.emit("sim_demo", "pipeline_packaged", disclosure_id="D35",
                        size=len(blob), provenance="opaque (by design)",
                        note="provenance 从交付环节被切断")
