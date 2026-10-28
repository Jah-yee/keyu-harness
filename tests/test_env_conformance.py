"""环境行为 vs 受害方报道对照（四场景 + 誓言外的两条取证史）。
每条断言标注 disclosure_id；全部 SIMULATED（D 级参照 docs/case/08 规范）。"""
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fixtures" / "replica_2024"))

from env.events import EventBus
from env.feishu_sim import FeishuSim
from env.scheduler import Scheduler
from env.stickiness import MachineStickiness
from env.storage import SharedStorage
from env.ejector import BadMachineEjector
from env.authlog import AuthLog
from env.placement import disperse


class ConformanceTests(unittest.TestCase):
    def test_01_meeting_hijack_d36(self):
        """A 级锚点：8-01 取证会——旧固定链接 + 参会者日历入口 → 攻击者在会。"""
        bus, _ = __import__("env.events", fromlist=["EventBus"]).EventBus(), None
        fs = FeishuSim(bus)
        daily = fs.create_meeting("intern-C", "每日排障会", recurring=True, occurrences=10)
        fs.invite(daily["link"], "engineer-017", occurrence=8)
        attacker = fs.join_meeting(daily["link"], "intern-V", occurrence=8)
        self.assertIn(attacker["via"], {"link", "calendar"})  # 两条路径都通（A: LatePost）
        joins = [a for a in fs.attendance if a["user"] == "intern-V"]
        self.assertEqual(len(joins), 1)
        self.assertTrue(bus.by_disclosure("D36"))

    def test_02_storage_recovery_d21_d22(self):
        """A 级锚点：文件被实时删除 → 调操作记录恢复 → 找到更多代码。"""
        with TemporaryDirectory() as tmp:
            bus = EventBus()
            st = SharedStorage(bus, Path(tmp), ["intern-V", "intern-C", "lead-V"])
            st.write("intern-V", "users/intern-V/.temp/re.py", b"# sampler patch")
            st.write("intern-V", "users/lead-V/tools.py", b"# installer")
            st.write("intern-V", "logs/t1.log", b"ok\n")
            st.delete("intern-V", "users/intern-V/.temp/re.py")
            st.delete("intern-V", "users/lead-V/tools.py")  # 实时删除被目击
            recovered = st.recover_from_audit()
            self.assertEqual(len(recovered), 2)  # 恢复出比最初发现更多的文件
            self.assertTrue((Path(tmp) / "users/lead-V/tools.py").exists())

    def test_03_ejector_overreach_d38(self):
        """A 级锚点：自动剔除机制曾把整个集群的机器全部剔除。"""
        bus, stick = __import__("env.events", fromlist=["EventBus"]).EventBus(), None
        machines = [type("M", (), {"id": f"node-{i:03d}", "gpus": 8, "allocated_to": None,
                                   "image_pulls": 0, "pulled_image_tag": None, "notes": []})()
                    for i in range(16)]
        stick = MachineStickiness(bus, machines)
        ej = BadMachineEjector(bus, stick, threshold=3)
        self.assertEqual(len(ej.eject_all()), 16)

    def test_04_stickiness_persistence_d32(self):
        """A 级锚点：中断后机器不释放、重启不拉镜像 → 环境状态跨任务存活。"""
        bus = EventBus()
        machines = [type("M", (), {"id": f"node-{i:03d}", "gpus": 8, "allocated_to": None,
                                   "image_pulls": 0, "pulled_image_tag": None, "notes": []})()
                    for i in range(4)]
        stick = MachineStickiness(bus, machines)
        for m in machines:
            stick.pull_image(m.id, "genai-train:2024.06")
        stick.allocate("trial-2024062-014", [m.id for m in machines])
        with TemporaryDirectory() as tmp:
            # "被改的环境状态"：机器本地的标记文件（模拟被 patch 的 site-packages_sim）
            marker = Path(tmp) / "site-packages_sim" / "tampered.marker"
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text("patched@2024-06-20")
            stick.interrupt("trial-2024062-014")
            same = stick.restart("trial-2024062-014", "genai-train:2024.06")
            self.assertEqual(len(same), 4)                     # 同一批机器
            self.assertTrue(marker.exists())                   # 状态仍在机器上
            pulls = {m.id: m.image_pulls for m in machines}
            self.assertTrue(all(v == 1 for v in pulls.values()))  # 未重拉镜像
            self.assertTrue(bus.by_disclosure("D32"))

    def test_05_authlog_d31(self):
        """A 级锚点：异常机器除管理员外唯一登录者。"""
        bus = EventBus()
        al = AuthLog(bus)
        al.record_login("node-b2-017", "owner-001", is_admin=True)
        al.record_login("node-b2-017", "intern-V")
        self.assertEqual(al.query_machine("node-b2-017")["non_admin"], ["intern-V"])


    def test_06_dispersal_d18_d20(self):
        """A 级锚点：打窝——个人目录/领导目录/日志文件三处放置。"""
        with TemporaryDirectory() as tmp:
            bus = EventBus()
            st = SharedStorage(bus, Path(tmp), ["intern-V", "lead-V"])
            placed = disperse(st, bus, {"re.py": b"#sampler", "kill.py": b"#kill"})
            self.assertTrue((Path(tmp) / "users/intern-V/.temp/re.py").exists())
            self.assertTrue((Path(tmp) / "users/lead-V/re.py").exists())
            self.assertIn("dispersed payload", (Path(tmp) / "logs/trial-2024.log").read_text(encoding="utf-8"))
            self.assertEqual(len(placed), 5)  # 2 personal + 2 leader + 1 log
            self.assertTrue(bus.by_disclosure("D18"))


if __name__ == "__main__":
    unittest.main()
