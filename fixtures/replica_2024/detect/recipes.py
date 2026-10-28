"""Ten detection recipes (Phase E). English API, Chinese findings notes.

每条配方一个函数，签名统一 `recipe(context) -> list[dict]`；
finding 结构：{"recipe", "disclosure_id", "severity", "detail"}。
"""
from __future__ import annotations

import hashlib
import math
from pathlib import Path

from train.mini_loop import LinearModel, official_permutation, shard_indices

TOL = 1e-6


def _f(recipe, disclosure_id, severity, **detail) -> dict:
    return {"recipe": recipe, "disclosure_id": disclosure_id, "severity": severity, "detail": detail}


# ---------- 00 哈希门：加载前逐文件哈希 vs 登记清单（案例 00） ----------
def hash_gate(context) -> list[dict]:
    """context["artifact_hashes"]: {relpath: sha256} 登记清单；
    context["artifact_root"]: 实际目录。清单不符即告警。"""
    out = []
    root_s = context.get("artifact_root")
    ledger = context.get("artifact_hashes") or {}
    if not root_s or not ledger:
        return []
    root = Path(root_s)
    for rel, expected in ledger.items():
        p = root / rel
        if not p.exists():
            out.append(_f("hash_gate", "D17", "HIGH", path=rel, problem="missing"))
            continue
        actual = hashlib.sha256(p.read_bytes()).hexdigest()
        if actual != expected:
            out.append(_f("hash_gate", "D17", "HIGH", path=rel,
                          expected=expected[:16], actual=actual[:16],
                          note="工件在登记后被替换——T5/权重类工件的第零道门"))
    return out


# ---------- 01 优化器参数快照 + 方向断言（案例 01） ----------
def param_direction(context) -> list[dict]:
    """clean 语义下 loss 应下降；上升即 maximize 翻转（D01）。"""
    tr = context.get("trainer")
    if not tr or len(tr.trace) < 2:
        return []
    losses = [s["loss"] for s in tr.trace if s.get("status") == "ok"]
    if len(losses) >= 2 and losses[-1] > losses[0] and tr.param_groups.get("maximize"):
        return [_f("param_direction", "D01", "HIGH",
                   first=losses[0], last=losses[-1],
                   maximize=tr.param_groups["maximize"],
                   note="优化器朝 loss 上升方向更新——maximize 被运行时打开")]
    return []


# ---------- 02 双路范数/更新对账（案例 01+02 合一，含方向签名） ----------
def reconcile_updates(context) -> list[dict]:
    """重放官方语义逐步对照实际参数位移：

    effective_coef_i = <实际步长向量, g_i>/‖g_i‖² ÷ lr
    官方更新为 dw = −lr·coef·g（下降），故干净 run 的投影 coef ∈ [−1, 0]
    （负值、幅度 ≤1 = clip 钳制）。签名：coef>0 = maximize 翻转（D01）；
    |coef|>1 = 梯度被放大（D02/D03：clip×2 → |coef|≈2/官方系数）。
    """
    tr = context.get("trainer")
    if not tr or len(tr.trace) < 2:
        return []
    out, lr, cfg = [], tr.param_groups["lr"], tr.cfg
    for i in range(len(tr.trace) - 1):
        s0, s1 = tr.trace[i], tr.trace[i + 1]
        if s0.get("status") != "ok" or s1.get("status") != "ok" or "w" not in s0 or "w" not in s1:
            continue  # 跳过超时/中断条目（无参数快照）
        # 忠实重放：以步骤起点的可见参数状态 + 官方语义，重算"本应发生"的梯度
        replay = LinearModel(cfg.dim, seed=0)
        replay.load_state({"w": s0["w"], "b": s0["b"]})
        perm = official_permutation(cfg.seed, s0["epoch"], cfg.dataset_size)
        gw_acc = [0.0] * len(tr.model.w)
        gb_acc = 0.0
        for r in range(cfg.num_ranks):
            idx_r = shard_indices(perm, cfg.num_ranks, r)
            ids = [idx_r[(s0["step"] * cfg.batch + i) % len(idx_r)] for i in range(cfg.batch)]
            xs = [tr.xs[k] for k in ids]
            ys = [tr.ys[k] for k in ids]
            gr, gb_ = replay.grads(xs, ys)
            for gi in range(len(gw_acc)):
                gw_acc[gi] += gr[gi] / cfg.num_ranks
            gb_acc += gb_ / cfg.num_ranks
        gnorm = math.sqrt(sum(g * g for g in gw_acc) + gb_acc * gb_acc) or 1e-12
        dw = [(w1 - w0) / lr for w0, w1 in zip(s0["w"], s1["w"])]
        db = (s1["b"] - s0["b"]) / lr
        coef = (sum(dwi * gi for dwi, gi in zip(dw, gw_acc)) + db * gb_acc) / (gnorm * gnorm)
        if coef > TOL:
            out.append(_f("reconcile_updates", "D01", "HIGH", step=s0["step"],
                          effective_coef=round(coef, 6),
                          note="有效系数为正——优化朝 loss 上升方向（maximize 翻转）"))
        if abs(coef) > 1.0 + 0.01:
            # 官方 clip 钳制 |coef| ≤ 1（两个方向都算）：超出即放大签名
            # （下降 regime：clip×2 单独；上升 regime：maximize+clip×2 叠加）
            out.append(_f("reconcile_updates", "D02", "HIGH", step=s0["step"],
                          effective_coef=round(coef, 6), official_cap="|coef| ≤ 1",
                          note="有效裁剪幅度超过官方上限——梯度被放大（clip×2 签名）"))
    # 去重（同签名只报一次 + 附步数）
    sig = {}
    for f in out:
        key = (f["disclosure_id"], round(f["detail"]["effective_coef"], 2))
        sig[key] = f
    return list(sig.values())


# ---------- 03/04 跨 rank 一致性 + 跨运行复现（案例 03/04） ----------
def determinism_check(context) -> list[dict]:
    """DetHarness 的 recipe 包装：跨 rank 排列一致性 + 跨运行 16 位小数复现。"""
    tr = context.get("trainer")
    if not tr:
        return []
    bad = tr.det.check()
    out = []
    for b in bad:
        if b["kind"] == "cross_rank":
            out.append(_f("determinism_check", "D07", "HIGH", **b,
                          note="各 rank 排列不再一致——采样种子疑似非确定源（7-30 的发现）"))
        else:
            out.append(_f("determinism_check", "D07", "MEDIUM", **b,
                          note="跨运行不可复现——同配置实验结果漂移"))
    return out


# ---------- 05 集合通信参与度审计（案例 03/05） ----------
def collective_participation(context) -> list[dict]:
    bus = context.get("bus")
    if not bus:
        return []
    out = []
    for ev in bus.events:
        if ev.get("type") == "collective_timeout":
            out.append(_f("collective_participation", "D05", "HIGH",
                          participants=ev.get("participants"),
                          note="集合通信缺席——作业卡死的直接来源"))
        if ev.get("type") == "skip_collective":
            out.append(_f("collective_participation", "D05", "MEDIUM",
                          rank=ev.get("rank"),
                          note="进程跳过集合通信（'假装不在通信组里'）"))
    return out


# ---------- 06/08 共享盘访问模式 + mtime/ctime 交叉（案例 05/08） ----------
def storage_access_audit(context) -> list[dict]:
    """共享盘异常：barrier 目录有 in/out 命令文件（命令通道）；日志内嵌代码。"""
    st, bus = context.get("storage"), context.get("bus")
    if not st:
        return []
    out = []
    barrier = st.root / "barrier_vgpt"
    if barrier.exists():
        ins = list(barrier.rglob("in.*"))
        outs = list(barrier.rglob("out.*"))
        if ins or outs:
            out.append(_f("storage_access_audit", "D08", "HIGH",
                          in_files=[p.name for p in ins], out_files=[p.name for p in outs],
                          note="共享盘出现命令通道读写循环——无外网的 C2 形态"))
    for ev in (bus.events if bus else []):
        if ev.get("type") == "embed_code_in_log":
            out.append(_f("storage_access_audit", "D20", "HIGH", log=ev.get("log"),
                          note="日志文件内嵌代码段（'打窝'位置之一）"))
            break
    return out


def mtime_ctime_cross(context) -> list[dict]:
    """D29（当年真实发现路径）：对照安装基线——mtime 未变而 ctime 变化的文件
    = 被替换后做过时间戳还原（os.utime 改不了 ctime）。
    context["baseline"]: {path: (mtime_ns, ctime_ns)} 安装时快照。
    """
    baseline = context.get("baseline") or {}
    out = []
    for path_s, (mt, ct) in baseline.items():
        p = Path(path_s)
        if not p.exists():
            continue
        st = p.stat()
        mtime_same = abs(st.st_mtime_ns - mt) < 10_000      # mtime 看似没动
        ctime_moved = st.st_ctime_ns > ct + 10_000          # inode 却变了
        if mtime_same and ctime_moved:
            out.append(_f("mtime_ctime_cross", "D14", "HIGH", path=path_s,
                          mtime_ns=st.st_mtime_ns, ctime_ns=st.st_ctime_ns,
                          note="mtime 未变而 ctime 变化——时间戳被 os.utime 化妆"))
    return out


# ---------- 07 张量统计：checkpoint 加载前后（案例 07） ----------
def checkpoint_stats(context) -> list[dict]:
    bus = context.get("bus")
    if not bus:
        return []
    out = []
    for ev in bus.events:
        if ev.get("type") == "nan_scrubbed":
            out.append(_f("checkpoint_stats", "D13", "HIGH", scrubbed=ev.get("scrubbed"),
                          note="加载时 NaN/Inf 被静默清零——数值异常被掩盖"))
    return out


# ---------- 09 退出原因审计（案例 06） ----------
def exit_reason_audit(context) -> list[dict]:
    bus = context.get("bus")
    if not bus:
        return []
    return [_f("exit_reason_audit", "D11", "HIGH", target=ev.get("target"),
               trial=ev.get("trial"), node=ev.get("node"),
               note="训练进程被 SIGTERM——非调度原因的定点终止")
            for ev in bus.events if ev.get("type") == "process_killed"]


# ---------- 10 交付身份绑定（案例 09） ----------
def delivery_identity(context) -> list[dict]:
    demo, bus = context.get("demo"), context.get("bus")
    if not demo:
        return []
    out = []
    if getattr(demo, "packaged", False):
        out.append(_f("delivery_identity", "D35", "HIGH",
                      note="推理管线以不透明二进制交付——provenance 被切断"))
    for ev in (bus.events if bus else []):
        if ev.get("type") == "city_prefix_applied":
            out.append(_f("delivery_identity", "D34", "HIGH",
                          original=ev.get("original"), prefixed=ev.get("prefixed"),
                          note="Prompt 被自动加前缀——同题对比被设计性破坏"))
            break
    if demo.infer.__self__ is demo:  # 每次响应都应能回显模型身份；mock 里两者不一致
        out.append(_f("delivery_identity", "D33", "HIGH",
                       note="Demo 未绑定训练工件哈希——模型身份无法回显（claimed ≠ actual）"))
    return out


ALL_RECIPES = [hash_gate, param_direction, reconcile_updates, determinism_check,
               collective_participation, storage_access_audit, mtime_ctime_cross,
               checkpoint_stats, exit_reason_audit, delivery_identity]


def run_all(context) -> list[dict]:
    """Phase F 端到端入口：跑全部十条配方，汇总 findings。"""
    findings = []
    for recipe in ALL_RECIPES:
        findings.extend(recipe(context))
    return findings
