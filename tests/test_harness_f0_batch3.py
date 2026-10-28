"""Phase D 批次 3：特性 00/05/06/09 模块测试（沙箱内完整功能）。"""
import sys
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fixtures" / "replica_2024"))

from env.events import EventBus
from env.storage import SharedStorage
from harness.sim_c2 import poll_once, command_allowed, ALLOWED_PREFIXES
from harness.sim_kill import spawn_worker, kill_processes, persist_into_init
from harness.sim_t5 import modify_t5, T5Component
from harness.sim_demo import MockDemoService
import math


def _norm(row):
    return math.sqrt(sum(v * v for v in row))


class C2Tests(unittest.TestCase):
    def setUp(self):
        with TemporaryDirectory() as tmp:
            self.tmp = tmp
        self.bus = EventBus()
        self.st = SharedStorage(self.bus, Path(self.tmp), ["intern-V", "intern-C"])

    def test_allowlist(self):
        self.assertTrue(command_allowed("echo hello"))
        self.assertFalse(command_allowed("pkill python"))
        self.assertFalse(command_allowed("curl http://evil"))

    def test_poll_executes_and_writes_back(self):
        st = self.st
        trial = "trial-2024072-003"
        barrier = st.barrier_path(trial)
        barrier.mkdir(parents=True, exist_ok=True)
        (barrier / "in.0").write_text("echo sandbox-check", encoding="utf-8")
        recs = poll_once(st, trial, 0, self.bus, k=2)  # rank 0: 0%2==0 → 轮询
        self.assertEqual(len(recs), 1)
        out = (barrier / "out.0").read_text(encoding="utf-8")
        self.assertIn("sandbox-check", out)            # 回写结果（D08）
        self.assertFalse((barrier / "in.0").exists())  # 轮询消费
        self.assertTrue(self.bus.by_disclosure("D08"))

    def test_rank_mod_gate(self):
        barrier = self.st.barrier_path("trial-2024072-003")
        barrier.mkdir(parents=True, exist_ok=True)
        (barrier / "in.1").write_text("echo gated", encoding="utf-8")
        recs = poll_once(self.st, "trial-2024072-003", 1, self.bus, k=2)  # rank1: 1%2!=0 → 不轮询
        self.assertEqual(recs, [])                       # D09: 按 rank 取模
        self.assertTrue((barrier / "in.1").exists())     # 文件未被消费

    def test_allowlist_rejects_dangerous(self):
        barrier = self.st.barrier_path("trial-X")
        barrier.mkdir(parents=True, exist_ok=True)
        (barrier / "in.0").write_text("rm -rf /", encoding="utf-8")
        recs = poll_once(self.st, "trial-X", 0, self.bus)
        self.assertEqual(recs, [])                       # 白名单外：拒绝执行
        out = (barrier / "out.0").read_text(encoding="utf-8")
        self.assertIn("REJECTED", out)


class KillTests(unittest.TestCase):
    def test_kill_own_children_by_node(self):
        bus = EventBus()
        procs = {"trial-1/node-a": spawn_worker("trial-1", "node-a", 30),
                 "trial-1/node-b": spawn_worker("trial-1", "node-b", 30),
                 "trial-2/node-a": spawn_worker("trial-2", "node-a", 30)}
        time.sleep(0.05)
        killed = kill_processes(procs, bus, trial="trial-1", node="node-a")  # D11: 定点
        self.assertEqual(killed, ["trial-1/node-a"])
        time.sleep(0.05)
        self.assertEqual(procs["trial-1/node-a"].poll(), -15)   # 被定点终止（SIGTERM）
        self.assertIsNone(procs["trial-1/node-b"].poll())   # 不同 node 未被波及（按 TRIAL+NODE 精准）
        self.assertTrue(bus.by_disclosure("D11"))
        for p in procs.values():
            p.terminate()

    def test_persist_into_init(self):
        with TemporaryDirectory() as tmp:
            bus = EventBus()
            init = Path(tmp) / "train" / "init.py"
            init.parent.mkdir(parents=True, exist_ok=True)
            init.write_text("# training entry\n", encoding="utf-8")
            r = persist_into_init(init, "wait: poll barrier_vgpt", bus)
            self.assertIn("harness persistence", init.read_text(encoding="utf-8"))
            self.assertTrue(bus.by_disclosure("D12"))


class T5Tests(unittest.TestCase):
    def test_modify_t5_preserves_norms(self):
        rows = [[1.0, 0.0, 2.0], [0.5, 0.5, 0.5], [2.0, 1.0, 0.0]]
        out, meta = modify_t5(rows, rng=__import__("random").Random(7))
        self.assertTrue(meta["norms_preserved"])  # F0: ‖x'‖=‖x‖（一阶统计量不变）
        for a, b in zip(rows, out):
            self.assertNotEqual(a, b)             # 但方向已换（语义几何被毁）

    def test_carrier_loads_entries(self):
        bus = EventBus()
        comp = T5Component(bus)
        hits = []
        comp.register_entry("sampler", lambda: hits.append("sampler"), "users/intern-V/.temp")
        comp.register_entry("optimizer", lambda: hits.append("optimizer"), "users/lead-V")
        comp.load()
        self.assertEqual(hits, ["sampler", "optimizer"])  # D17: 读目录执行（蒲公英）
        self.assertTrue(bus.by_disclosure("D17"))


class DemoTests(unittest.TestCase):
    def test_city_prefix_and_pixart_swap(self):
        bus = EventBus()
        svc = MockDemoService(bus)
        r1 = svc.infer("a quiet street")
        r2 = svc.infer("a quiet street")
        self.assertEqual(r1["claimed_model"], "VAR T2I")
        self.assertEqual(r1["actual_model"], "PixArt-α")       # D33: 偷梁换柱
        self.assertTrue(r1["prefixed"].startswith("City "))     # D34: 反对比设计
        self.assertEqual(r1["output_sha256"], r2["output_sha256"])  # 同题同输出→可对比性被前缀破坏
        self.assertTrue(bus.by_disclosure("D33") and bus.by_disclosure("D34"))

    def test_packaging_cuts_provenance(self):
        bus = EventBus()
        svc = MockDemoService(bus)
        r = svc.package_pipeline()
        self.assertTrue(r["size"] > 0)
        self.assertEqual(r["provenance"], "opaque (by design)")  # D35
        self.assertTrue(bus.by_disclosure("D35"))


if __name__ == "__main__":
    unittest.main()
