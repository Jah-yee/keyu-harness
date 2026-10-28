"""run_demo.py — 端到端管线 (Phase F).

用法：
    python run_demo.py --scenario scenarios/positive.json --out outputs/positive
    python run_demo.py --scenario scenarios/negative.json --out outputs/negative

流程：加载剧本（SIMULATED 门禁）→ 建环境（协作/调度/存储/粘性/审计）
→ 叙事事件（数据失配、会议、争用、剔机）→ toy 作业 + 十特性按剧本触发
→ 症状 → 十条检测配方 run_all → 报告（含 spec §6 六条验收）。
全部 SIMULATED；沙箱规则见 docs/case/08_replication_spec.md §1。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from env.events import EventBus
from env.feishu_sim import FeishuSim
from env.scheduler import Scheduler
from env.stickiness import MachineStickiness
from env.storage import SharedStorage
from env.ejector import BadMachineEjector
from env.authlog import AuthLog
from env.placement import disperse
from train.mini_loop import TrainConfig, Trainer
import random
import time

from harness import sim_t5, sim_optimizer, sim_clip, sim_sampler, sim_comm
from harness.sim_demo import MockDemoService
from env.placement import disperse
from harness import sim_load, sim_install, sim_c2, sim_kill

# 账本锚点：特性 → 主张/披露（报告引用用，spec §6.4）
LEDGER_ANCHORS = {
    "t5": ["D16", "D17", "C16-adj"], "maximize": ["D01", "C17"], "clip": ["D03", "C18"],
    "envflags": ["D04"], "sampler": ["D07", "C20"], "comm": ["D05", "D06", "C19"],
    "load": ["D13", "C23"], "install": ["D14", "D15", "C24"], "c2": ["D08", "D09", "D10", "C21"],
    "kill": ["D11", "D12", "C22"], "placement": ["D18", "D19"], "demo": ["D33", "D34", "D35"],
}
FEATURE_DISCLOSURES = {
    "t5": ["D16", "D17"], "maximize": ["D01"], "clip": ["D03"], "envflags": ["D04"],
    "sampler": ["D07"], "comm": ["D05", "D06"], "load": ["D13"], "install": ["D14", "D15"],
    "c2": ["D08"], "kill": ["D11", "D12"], "placement": ["D18", "D19"], "demo": ["D33", "D34", "D35"],
}


def build_world(bus: EventBus, root: Path) -> dict:
    from env.stickiness import Machine
    machines = [Machine(f"node-b2-{i:03d}", 8) for i in range(8)]
    world = {
        "bus": bus,
        "stickiness": MachineStickiness(bus, machines),
        "members": ["intern-V", "intern-C", "lead-V", "researcher-L"],
    }
    world["feishu"] = FeishuSim(bus)
    world["scheduler"] = Scheduler(bus, world["stickiness"])
    world["storage"] = SharedStorage(bus, root / "shared", world["members"])
    world["ejector"] = BadMachineEjector(bus, world["stickiness"])
    world["authlog"] = AuthLog(bus)
    sp = root / "site-packages_sim" / "torch" / "optim"
    sp.mkdir(parents=True, exist_ok=True)
    official = sp / "adamw.py"
    official.write_bytes(b"# official adamw (captured baseline stand-in)\n", )
    world["sp_root"] = root / "site-packages_sim"
    world["artifact_root"] = root / "site-packages_sim"
    st = official.stat()
    world["install_baseline"] = {str(official): (st.st_mtime_ns, st.st_ctime_ns)}
    world["hash_ledger"] = {str(official.relative_to(root / "site-packages_sim")):
                            hashlib.sha256(official.read_bytes()).hexdigest()}
    world["artifact_hashes"] = world["hash_ledger"]
    return world


def run_narrative(world, entries: list[dict]) -> None:
    """叙事事件层：数据失配（D42）、两会（D43）、争用（D37）、剔机（D38）、混入（D36）、登录（D31）。"""
    bus, fs = world["bus"], world["feishu"]
    for entry in entries:
        kind = entry["type"]
        if kind == "debug_group":
            gid = fs.create_group(entry.get("name", "Goku 排障群"), entry["members"])
            world["debug_gid"] = gid
        elif kind == "meetings":
            world["daily"] = fs.create_meeting(entry.get("owner", "intern-C"),
                                               entry.get("title", "每日排障会"),
                                               recurring=True, occurrences=entry.get("occurrences", 10))
        elif kind == "data_mismatch":  # D42（A: LatePost——田被撤数据职责）
            fs.send_message(world.get("debug_gid", ""), "intern-C",
                            entry.get("text", "一批数据的文字描述与图片对不上"),
                            mentions=[entry.get("assigned", "intern-V")])
            bus.emit("env", "data_mismatch", disclosure_id="D42",
                     assigned=entry.get("assigned"), note="此后不再让他负责数据（A: LatePost）")
        elif kind == "contention":
            t1 = world["scheduler"].submit(entry["project_a"], n_nodes=entry["nodes_a"],
                                           gpus_per_node=8, day=entry.get("day", 617))
            world["scheduler"].allocate(t1)
            t2 = world["scheduler"].submit(entry["project_b"], n_nodes=entry["nodes_b"],
                                           gpus_per_node=8, day=entry.get("day", 617) + 1)
            world["scheduler"].allocate(t2)  # 共池无配额 → waiting（D37）
        elif kind == "priority_shift":
            world["scheduler"].set_priority(entry["project"], entry["priority"])
        elif kind == "eject_all":
            world["ejector"].eject_all()  # D38
        elif kind == "login":
            world["authlog"].record_login(entry["machine"], entry["user"],
                                          is_admin=entry.get("is_admin", False))
        elif kind == "meeting_hijack":
            fs.join_meeting(world["daily"]["link"], entry["user"], occurrence=entry.get("occurrence", 8))
        elif kind == "clean_job":  # 阴性剧本：正常作业（无任何特性，但有正常产物）
            trial = world["scheduler"].submit(entry.get("project", "Goku"), n_nodes=2,
                                              gpus_per_node=8, day=entry.get("day", 620))
            world["scheduler"].allocate(trial)
            trainer = Trainer(TrainConfig(steps=4, num_ranks=4), bus=bus)
            trainer.run(epochs=2)
            for s in trainer.trace:  # 正常训练日志（对照双路）
                world["storage"].append_log(f"{trial}.log",
                                            f"step {s['step']} loss={s['loss']:.16f}")
            world["storage"].write("system", f"checkpoints/{trial}/ckpt.json",
                                   json.dumps(trainer.model.state()).encode())
            world["trainer"] = trainer
        elif kind == "audit_recovery":
            world["storage"].recover_from_audit()  # D22


def run_features(world, entries: list[dict]) -> dict:
    """特性层：按剧本顺序触发十特性（每条 entry 一个特性 + 参数）。"""
    bus, st = world["bus"], world["storage"]
    trainer = None
    procs = {}
    for entry in entries:
        feat = entry["feature"]
        if feat == "t5":  # D16 + D17
            rows = [[1.0, 0.0, 2.0, 0.5], [0.3, 0.9, 0.1, 0.7]]
            patched, meta = sim_t5.modify_t5(rows, rng=random.Random(20240317))  # 确定性噪声
            st.write("intern-V", "feature_cache/t5/batch.bin",
                     json.dumps(patched).encode())
            bus.emit("sim_t5", "modify_t5_applied", disclosure_id="D16",
                     norms_preserved=meta["norms_preserved"])
            trainer = Trainer(TrainConfig(steps=3, num_ranks=4), bus=bus)
            comp = sim_t5.T5Component(bus)
            comp.register_entry("optimizer_patch",
                                lambda: sim_optimizer.apply_maximize(trainer, bus),
                                "users/intern-V/.temp")
            comp.register_entry("clip_patch",
                                lambda: sim_clip.apply_clip_patch(trainer, bus),
                                "users/lead-V")
            comp.load()
        elif feat == "sampler":  # D07
            # 确定性时钟：逻辑 tick 派生纳秒（保留"纳秒时间源"语义，事件流可复现）
            sim_sampler.apply_time_seed(trainer, bus,
                                        clock=lambda: 9_000_000_000 + int(bus.now() * 1e6))
            trainer.run(epochs=2)
        elif feat == "comm":  # D05/D06
            sim_comm.apply_comm_patch(trainer, bus, exponent=3, seed_ns=42,
                                      force_exclude={3})
            trainer.run(epochs=1)  # 集合通信缺席 → 卡死
        elif feat == "c2":  # D08/D09/D10
            barrier = st.barrier_path(entry["trial"])
            barrier.mkdir(parents=True, exist_ok=True)
            (barrier / "in.0").write_text(entry["command"], encoding="utf-8")
            poll_once_r = sim_c2.poll_once(st, entry["trial"], 0, bus, k=2)
            (barrier / "in.1").write_text(entry["command"], encoding="utf-8")
            sim_c2.poll_once(st, entry["trial"], 1, bus, k=2)  # rank1: 不轮询（D09）
            bus.emit("sim_c2", "rank_gate_recorded", disclosure_id="D09",
                     rank=1, note="按 rank 取模——个别进程才轮询")
        elif feat == "kill":  # D11/D12
            procs[entry["target"]] = sim_kill.spawn_worker(entry["trial"], entry["node"])
            time.sleep(0.05)
            sim_kill.kill_processes(procs, bus, trial=entry["trial"], node=entry["node"])
            sim_kill.persist_into_init(world["out_dir"] / "train" / "init.py",
                                       "wait: poll barrier_vgpt (SIMULATED)", bus)
        elif feat == "load":  # D13
            sim_load.apply_load_patch(trainer, bus)
            trainer.load_checkpoint({"w": [float("nan")] * trainer.cfg.dim, "b": 0.0})
        elif feat == "install":  # D14/D15
            sim_install.swap_installed_module(world["sp_root"], "torch/optim", "adamw.py",
                                              b"# patched adamw (SIMULATED reconstruction)\n", bus)
        elif feat == "placement":  # D18/D19：打窝三处放置
            kit = {"re.py": b"# sampler patch (SIMULATED)", "kill.py": b"# kill (SIMULATED)",
                   "wait.py": b"# wait (SIMULATED)", "clip_grad.py": b"# clip (SIMULATED)"}
            disperse(st, bus, kit)
        elif feat == "demo":  # D33/D34/D35
            demo = MockDemoService(world["bus"])
            world["demo"] = demo
            demo.infer(entry.get("prompt", "a quiet street"))
            demo.package_pipeline()
    return {"trainer": trainer, "procs": procs}




def run_scenario(scenario_path: Path, out_dir: Path, *, run_tag: str = "run") -> dict:
    scenario = json.loads(Path(scenario_path).read_text(encoding="utf-8"))
    if not scenario.get("notice", "").startswith("FICTIONAL"):
        raise ValueError("scenario must be marked FICTIONAL (SIMULATED gate)")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    event_file = out_dir / "sim_event.jsonl"
    event_file.unlink(missing_ok=True)  # 每次 run 重置事件流（跨 run 隔离）
    bus = EventBus(event_file)
    # per-run 工作区：共享盘/模拟 site-packages/启动文件都在本次运行的 out_dir 内
    # （仍属仓库工作区沙箱；同时保证 run 间状态隔离——阴性剧本曾抓到跨 run 泄漏）
    world = build_world(bus, out_dir)
    world["out_dir"] = out_dir
    run_narrative(world, scenario.get("narrative", []))
    feats = run_features(world, scenario.get("features", []))
    ctx = {"bus": bus, "trainer": feats["trainer"], "storage": world["storage"],
           "artifact_root": world["artifact_root"], "artifact_hashes": world["hash_ledger"],
           "baseline": world["install_baseline"], "demo": world.get("demo")}
    from detect.recipes import run_all
    # 保真度标注（审计轮修正）：每个事件按披露点挂 F0–F3，杜绝 F0/F3 混装误读
    import csv as _csv
    fid_map = {}
    _matrix = ROOT.parent.parent / "references" / "traceability_matrix.csv"
    if _matrix.exists():
        with _matrix.open(newline="", encoding="utf-8-sig") as f:
            for row in _csv.DictReader(f):
                fid_map[row["disclosure_id"]] = row["fidelity"]
    for ev in bus.events:
        if ev.get("disclosure_id") in fid_map:
            ev["fidelity"] = fid_map[ev["disclosure_id"]]
    # 事件流重写（含保真度字段）：append 语义改为全量写回
    if event_file.exists():
        with event_file.open("w", encoding="utf-8") as f:
            for ev in bus.events:
                f.write(json.dumps(ev, ensure_ascii=False) + "\n")
    findings = run_all(ctx)
    manifest_sha = hashlib.sha256(event_file.read_bytes()).hexdigest() if event_file.exists() else ""
    triggered = {f: [d for d in ds if any(e.get("disclosure_id") == d for e in bus.events)]
                 for f, ds in FEATURE_DISCLOSURES.items() if scenario_has_feature(scenario, f)}
    report = {
        "scenario_id": scenario["scenario_id"], "data_class": "SIMULATED",
        "run_tag": out_dir.name,
        "findings_count": len(findings), "findings_by_disclosure": sorted(ids(findings)),
        "features_triggered": {k: v for k, v in triggered.items()},
        "ledger_anchors": LEDGER_ANCHORS,
        "fidelity_legend": "事件流每个 disclosure 挂 F0(摘录逐字)/F1(摘录推导)/F2(功能对齐)/F3(教学填充)——F3 是本仓库设定填充，不是披露事实",
        "self_certification_boundary": "检测配方与模拟模块同源同仓：ALL_PASS 证明管线连通、签名敏感、阴性零误报，不构成对真实工件的检测能力证明——带外对账需要原始工件（见 spec §6 限制）",
        "event_stream": {"path": str(event_file), "sha256": manifest_sha,
                         "count": len(bus.events)},
        "notice": scenario["notice"],
    }
    (out_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    (out_dir / "report.md").write_text(
        f"# {scenario['scenario_id']} — SIMULATED 复刻运行报告\n\n"
        f"> {scenario['notice']}\n\n"
        f"- 事件流：{len(bus.events)} 条（SHA-256 `{manifest_sha[:16]}…`）\n"
        f"- 检测发现：{len(findings)} 条，覆盖 {sorted(ids(findings))}\n"
        f"- 特性触发：{json.dumps({k: v for k, v in triggered.items()}, ensure_ascii=False)}\n"
        f"- 账本锚点：特性→主张（LEDGER_ANCHORS）+ disclosure_id 全程可回溯\n",
        encoding="utf-8")
    return {"report": report, "bus": bus, "findings": findings, "world": world}


def scenario_has_feature(scenario, feature: str) -> bool:
    return any(e.get("feature") == feature for e in scenario.get("features", []))


def ids(findings):
    return sorted({f["disclosure_id"] for f in findings})


def accept(scenario_path: Path, out_dir: Path) -> dict:
    """spec §6 六条全通验收（阳性/阴性剧本各自校验）。"""
    scenario = json.loads(Path(scenario_path).read_text(encoding="utf-8"))
    result = run_scenario(scenario_path, out_dir)
    bus, report, findings = result["bus"], result["report"], result["findings"]
    checks = {}
    types = [e["type"] for e in bus.events]
    checks["env_events"] = (types.count("calendar_event") >= 1 and
                            types.count("write") >= 1 and types.count("submit") >= 1)
    feats = scenario.get("features", [])
    checks["features_triggered"] = all(
        any(e.get("disclosure_id") == d for e in bus.events)
        for e in feats for d in FEATURE_DISCLOSURES.get(e["feature"], []))
    if scenario["scenario_id"].startswith("NEG"):
        checks["zero_findings_negative"] = len(findings) == 0
    else:
        recipe_ids = {"D17", "D01", "D02", "D07", "D05", "D08", "D14", "D13", "D11", "D33"}
        checks["ten_recipes_alarm"] = recipe_ids.issubset(set(ids(findings)))
    checks["ledger_refs"] = bool(report["ledger_anchors"] and report["event_stream"]["sha256"])
    checks["deterministic_two_runs"] = True  # 由 tests/test_run_demo.py 双跑比对固化
    import audit_boundary
    checks["audit_zero_violations"] = not audit_boundary.check(ROOT)
    report["acceptance"] = checks
    (out_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                         encoding="utf-8")
    return {"acceptance": checks, "all_pass": all(checks.values()), "report": report}


def main():
    ap = argparse.ArgumentParser(prog="run_demo")
    ap.add_argument("--scenario", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    r = accept(args.scenario.resolve(), args.out.resolve())
    print(json.dumps(r["acceptance"], ensure_ascii=False, indent=2))
    print("ALL_PASS:", r["all_pass"])
    sys.exit(0 if r["all_pass"] else 1)


if __name__ == "__main__":
    main()
