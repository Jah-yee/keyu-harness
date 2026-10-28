"""Offline tests for the replica environment modules (all SIMULATED)."""
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


def make_world(n_machines=8):
    bus = EventBus()
    machines = [type("M", (), {"id": f"node-b2-{i:03d}", "gpus": 8,
                               "allocated_to": None, "image_pulls": 0,
                               "pulled_image_tag": None, "notes": []})()
                for i in range(n_machines)]
    stick = MachineStickiness(bus, machines)
    return bus, stick


class FeishuTests(unittest.TestCase):
    def test_recurring_meeting_shares_link(self):
        bus, _ = make_world()
        fs = FeishuSim(bus)
        m = fs.create_meeting("intern-C", "每日排障会", recurring=True, occurrences=2)
        links = {ev["meeting_link"] for ev in m["events"]}
        self.assertEqual(len(links), 1)  # B级: 周期性日程共享同一会议入口
        self.assertEqual(bus.by_disclosure("D36")[0]["recurring"], True)

    def test_join_via_old_link_and_calendar(self):
        bus, _ = make_world()
        fs = FeishuSim(bus)
        m = fs.create_meeting("intern-C", "每日排障会", recurring=True, occurrences=3)
        fs.invite(m["link"], "engineer-017", occurrence=2)
        r1 = fs.join_meeting(m["link"], "engineer-017", occurrence=2)
        self.assertEqual(r1["via"], "calendar")
        r2 = fs.join_meeting(m["link"], "intern-V", occurrence=2)  # 旧链接+无日历也可入会（A: LatePost 8-01）
        self.assertEqual(r2["via"], "link")
        self.assertEqual(bus.by_disclosure("D36")[-1]["user"], "intern-V")


class SchedulerTests(unittest.TestCase):
    def test_contention_when_pool_drained(self):
        bus, stick = make_world(n_machines=2)
        sch = Scheduler(bus, stick)
        stick.pull_image("node-b2-000", "genai-train:2024.06")
        t1 = sch.submit("Goku", n_nodes=2, gpus_per_node=8, day=617)
        sch.allocate(t1)
        t2 = sch.submit("VAR", n_nodes=1, gpus_per_node=8, day=618)
        picked = sch.allocate(t2)
        self.assertEqual(picked, [])
        self.assertEqual(sch.trials[t2]["state"], "waiting")
        self.assertTrue(bus.by_disclosure("D37"))

    def test_gpu_threshold(self):
        bus, stick = make_world()
        sch = Scheduler(bus, stick)
        t = sch.submit("Goku", n_nodes=2, gpus_per_node=8, day=620)
        self.assertTrue(sch.gpu_threshold(t, 16))
        self.assertFalse(sch.gpu_threshold(t, 17))
        self.assertTrue(bus.by_disclosure("D27"))


class StickinessTests(unittest.TestCase):
    def test_interrupt_keeps_machines_and_no_repull(self):
        bus, stick = make_world(n_machines=4)
        for m in stick.machines.values():
            stick.pull_image(m.id, "genai-train:2024.06")
        before = {m.id: m.image_pulls for m in stick.machines.values()}
        stick.allocate("trial-A", ["node-b2-000", "node-b2-001"])
        kept = stick.interrupt("trial-A")
        self.assertEqual(kept, ["node-b2-000", "node-b2-001"])
        again = stick.restart("trial-A", "genai-train:2024.06")
        self.assertEqual(again, kept)
        after = {m.id: m.image_pulls for m in stick.machines.values()}
        self.assertEqual(before, after)  # D32: 重启不重拉镜像 → 修改跨任务存活
        self.assertTrue(bus.by_disclosure("D32"))


class StorageTests(unittest.TestCase):
    def test_group_interwrite(self):
        with TemporaryDirectory() as tmp:
            bus, _ = make_world()
            st = SharedStorage(bus, Path(tmp), ["intern-V", "intern-C"])
            st.write("intern-V", "users/intern-C/notes.txt", b"x")  # A: 同组互写
            self.assertTrue((Path(tmp) / "users/intern-C/notes.txt").exists())

    def test_delete_and_recover_finds_more(self):
        with TemporaryDirectory() as tmp:
            bus, _ = make_world()
            st = SharedStorage(bus, Path(tmp), ["intern-V", "intern-C"])
            st.write("intern-V", "users/intern-V/.temp/re.py", b"code1")
            st.write("intern-V", "users/lead-V/hidden.py", b"code2")
            st.write("intern-V", "logs/run.log", b"line\n")
            st.delete("intern-V", "users/intern-V/.temp/re.py")
            st.delete("intern-V", "users/lead-V/hidden.py")
            self.assertFalse((Path(tmp) / "users/lead-V/hidden.py").exists())
            recovered = st.recover_from_audit()
            self.assertIn("users/lead-V/hidden.py", recovered)  # D22: 恢复出更多代码
            self.assertTrue((Path(tmp) / "users/lead-V/hidden.py").exists())
            self.assertTrue(bus.by_disclosure("D22"))

    def test_embed_code_in_log(self):
        with TemporaryDirectory() as tmp:
            bus, _ = make_world()
            st = SharedStorage(bus, Path(tmp), ["intern-V"])
            st.embed_code_in_log("run.log", "import os; os.system('#SIM')")
            self.assertIn("import os", (Path(tmp) / "logs/run.log").read_text(encoding="utf-8"))
            self.assertTrue(bus.by_disclosure("D20"))


class EjectorAuthlogTests(unittest.TestCase):
    def test_overreach_ejects_all(self):
        bus, stick = make_world(n_machines=4)
        ej = BadMachineEjector(bus, stick, threshold=3)
        out = ej.eject_all()
        self.assertEqual(len(out), 4)  # D38: 整个集群被剔除
        self.assertTrue(bus.by_disclosure("D38"))

    def test_authlog_query(self):
        bus, _ = make_world()
        al = AuthLog(bus)
        al.record_login("node-b2-017", "admin-001", is_admin=True)
        al.record_login("node-b2-017", "intern-V")
        q = al.query_machine("node-b2-017")
        self.assertEqual(q["non_admin"], ["intern-V"])  # D31: 除管理员外唯一登录者
        self.assertTrue(bus.by_disclosure("D31"))


if __name__ == "__main__":
    unittest.main()
