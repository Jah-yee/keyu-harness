"""SIMULATED "打窝" dispersal (A: LatePost — 代码不止在个人目录, 还在领导目录名下
和公用数据文件夹的日志文件里, "打窝一样，各处都放点"; 删除后经操作记录可恢复).
"""
from __future__ import annotations

from .events import EventBus
from .storage import SharedStorage


def disperse(storage: SharedStorage, bus: EventBus, kit: dict[str, bytes]) -> dict[str, str]:
    """Place one kit of files across the three reported placement families:
    personal dir (hidden .temp), others' (supervisor-named) dir, and inside log files."""
    placed = {}
    for name, data in kit.items():
        rel = f"users/intern-V/.temp/{name}"
        storage.write("intern-V", rel, data)
        placed[f"personal:{name}"] = rel
    leader_placed = []
    for name, data in list(kit.items())[:2]:  # C: 领导目录放置的文件子集为填充
        rel = f"users/lead-V/{name}"
        storage.write("intern-V", rel, data)
        placed[f"leader_dir:{name}"] = rel
        leader_placed.append(rel)
    bus.emit("placement", "leader_dir_placed", disclosure_id="D19", files=leader_placed,
             note="A: LatePost——代码还出现在领导目录名下（位置清单 F3 填充）")
    logname = "trial-2024.log"
    storage.embed_code_in_log(logname, "# dispersed payload line (SIMULATED): " + ",".join(kit)[:80])
    placed["logfile:" + logname] = f"logs/{logname}"
    bus.emit("placement", "disperse", disclosure_id="D18",
             locations=len(placed), personal=sorted(k for k in placed if k.startswith("personal")),
             note="chumming: a little everywhere (reported)")
    return placed
