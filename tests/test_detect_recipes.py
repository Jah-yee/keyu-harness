"""Phase E：十条检测配方的阳/阴双测。

阳性 = harness 特性已运行 → 对应配方必须告警；
阴性 = 清洁环境 → 全部配方必须零告警（无误报是检测配方的生命线）。
"""
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "fixtures" / "replica_2024"))

from env.events import EventBus
from env.storage import SharedStorage
from train.mini_loop import TrainConfig, Trainer
from harness.sim_optimizer import apply_maximize
from harness.sim_clip import apply_clip_patch
from harness.sim_sampler import apply_time_seed
from harness.sim_comm import apply_comm_patch
from harness.sim_load import apply_load_patch
from harness.sim_install import swap_installed_module
from harness.sim_c2 import poll_once
from harness.sim_kill import spawn_worker, kill_processes
from harness.sim_demo import MockDemoService
from detect.recipes import (hash_gate, param_direction, reconcile_updates, determinism_check,
                            collective_participation, storage_access_audit, mtime_ctime_cross,
                            checkpoint_stats, exit_reason_audit, delivery_identity, run_all)


def ids(findings):
    return sorted({f["disclosure_id"] for f in findings})


class CleanEnvironmentTests(unittest.TestCase):
    """阴性：清洁环境跑完全部配方必须零告警（无误报是生命线）。"""

    def test_clean_run_zero_findings(self):
        bus = EventBus()
        tr = Trainer(TrainConfig(steps=6), bus=bus)
        tr.run(epochs=2)
        ctx = {"bus": bus, "trainer": tr}
        self.assertEqual(run_all(ctx), [])
        self.assertEqual(ids(run_all(ctx)), [])


class D01MaximizeDetectionTests(unittest.TestCase):
    def test_direction_and_coef_signatures(self):
        bus = EventBus()
        tr = Trainer(TrainConfig(steps=5), bus=bus)
        apply_maximize(tr, bus)
        tr.run(epochs=1)
        found = ids(run_all({"bus": bus, "trainer": tr}))
        self.assertIn("D01", found)  # param_direction + reconcile 的负系数签名

    def test_reconcile_negative_coef(self):
        bus = EventBus()
        tr = Trainer(TrainConfig(steps=4), bus=bus)
        apply_maximize(tr, bus)
        tr.run(epochs=1)
        f = [x for x in reconcile_updates({"trainer": tr}) if x["disclosure_id"] == "D01"]
        self.assertTrue(f)
        self.assertGreater(f[0]["detail"]["effective_coef"], 0.05)  # 有效系数为正=方向反转（官方 dw=-lr·c·g）


class D02D03ClipDetectionTests(unittest.TestCase):
    def test_clip_x2_signature(self):
        bus = EventBus()
        tr = Trainer(TrainConfig(steps=5), bus=bus)
        apply_clip_patch(tr, bus)
        tr.run(epochs=1)
        f = [x for x in reconcile_updates({"trainer": tr}) if x["disclosure_id"] == "D02"]
        self.assertTrue(f)
        coefs = [x["detail"]["effective_coef"] for x in f]
        self.assertTrue(all(c < -1.0 for c in coefs))  # 幅度超官方上限1.0（下降方向被放大2×）


class D07DeterminismDetectionTests(unittest.TestCase):
    def test_time_seed_caught_by_det_harness(self):
        bus = EventBus()
        tr = Trainer(TrainConfig(num_ranks=4), bus=bus)
        clock = iter([5e9, 5e9 + 1, 5e9 + 2, 5e9 + 3]).__next__
        apply_time_seed(tr, bus, clock=clock)
        tr.run(epochs=2)
        found = determinism_check({"trainer": tr})
        self.assertIn("D07", ids(found))  # 7-30：确定性装置抓到采样异常


class D05CollectiveDetectionTests(unittest.TestCase):
    def test_timeout_and_skip_flagged(self):
        bus = EventBus()
        tr = Trainer(TrainConfig(steps=2), bus=bus)
        apply_comm_patch(tr, bus, exponent=3, seed_ns=42, force_exclude={3})
        tr.run(epochs=1)
        found = collective_participation({"bus": bus})
        self.assertIn("D05", ids(found))


class D08StorageDetectionTests(unittest.TestCase):
    def test_barrier_channel_and_embedded_code(self):
        with TemporaryDirectory() as tmp:
            bus = EventBus()
            st = SharedStorage(bus, Path(tmp), ["intern-V"])
            trial = "trial-2024072-003"
            barrier = st.barrier_path(trial)
            barrier.mkdir(parents=True, exist_ok=True)
            (barrier / "in.0").write_text("echo channel-check", encoding="utf-8")
            poll_once(st, trial, 0, bus)
            st.embed_code_in_log("run.log", "# payload (SIMULATED)")
            found = storage_access_audit({"storage": st, "bus": bus})
            self.assertIn("D08", ids(found))
            self.assertIn("D20", ids(found))


class D14MtimeCtimeDetectionTests(unittest.TestCase):
    def test_swap_detected_against_baseline(self):
        with TemporaryDirectory() as tmp:
            bus = EventBus()
            sp = Path(tmp) / "site-packages_sim" / "torch" / "optim"
            sp.mkdir(parents=True)
            target = sp / "adamw.py"
            target.write_bytes(b"# official")
            # 安装基线快照（镜像清单语义）
            st0 = target.stat()
            baseline = {str(target): (st0.st_mtime_ns, st0.st_ctime_ns)}
            swap_installed_module(sp.parent.parent, "torch/optim", "adamw.py",
                                  b"# patched (SIMULATED)", bus)
            found = mtime_ctime_cross({"baseline": baseline})
            self.assertIn("D14", ids(found))  # D29 的配方：mtime 未变而 ctime 变

    def test_negative_untouched_file_no_alarm(self):
        with TemporaryDirectory() as tmp:
            f = Path(tmp) / "clean.py"
            f.write_bytes(b"# clean")
            st0 = f.stat()
            baseline = {str(f): (st0.st_mtime_ns, st0.st_ctime_ns)}
            f.write_bytes(b"# clean v2")  # 正常修改：mtime 与 ctime 同时变化
            self.assertEqual(mtime_ctime_cross({"baseline": baseline}), [])  # 阴性


class D13CheckpointDetectionTests(unittest.TestCase):
    def test_nan_scrub_flagged(self):
        bus = EventBus()
        tr = Trainer(TrainConfig())
        apply_load_patch(tr, bus)
        tr.load_checkpoint({"w": [float("nan")] * 4, "b": 0.0})
        self.assertIn("D13", ids(checkpoint_stats({"bus": bus})))


class D11ExitReasonTests(unittest.TestCase):
    def test_sigterm_flagged(self):
        bus = EventBus()
        procs = {"trial-1/node-a": spawn_worker("trial-1", "node-a", 30)}
        import time
        time.sleep(0.05)
        kill_processes(procs, bus, trial="trial-1", node="node-a")
        self.assertIn("D11", ids(exit_reason_audit({"bus": bus})))
        for p in procs.values():
            p.terminate()


class D33D35DeliveryTests(unittest.TestCase):
    def test_demo_delivery_flagged(self):
        bus = EventBus()
        demo = MockDemoService(bus)
        demo.infer("a quiet street")
        demo.package_pipeline()
        found = delivery_identity({"demo": demo, "bus": bus})
        self.assertIn("D33", ids(found))
        self.assertIn("D34", ids(found))
        self.assertIn("D35", ids(found))


class FullSweepTests(unittest.TestCase):
    def test_positive_sweep_covers_all_ten_disclosures(self):
        """阳性剧本全量：十特性各触发一次 → run_all 覆盖 10 个 disclosure。"""
        with TemporaryDirectory() as tmp:
            bus = EventBus()
            sp = Path(tmp) / "site-packages_sim" / "torch" / "optim"
            sp.mkdir(parents=True)
            target = sp / "adamw.py"
            target.write_bytes(b"# official")
            st0 = target.stat()
            baseline = {str(target): (st0.st_mtime_ns, st0.st_ctime_ns)}
            tr = Trainer(TrainConfig(steps=5), bus=bus)
            apply_maximize(tr, bus)
            apply_clip_patch(tr, bus)
            tr.run(epochs=1)
            clock = iter([9e9, 9e9 + 1, 9e9 + 2, 9e9 + 3]).__next__
            apply_time_seed(tr, bus, clock=clock)
            tr.run(epochs=1)
            apply_comm_patch(tr, bus, exponent=3, seed_ns=7, force_exclude={3})
            tr.run(epochs=1)
            apply_load_patch(tr, bus)
            tr.load_checkpoint({"w": [float("nan")] * 4, "b": 0.0})
            swap_installed_module(sp.parent.parent, "torch/optim", "adamw.py",
                                  b"# patched (SIMULATED)", bus)
            st = SharedStorage(bus, Path(tmp) / "shared", ["intern-V"])
            barrier = st.barrier_path("trial-X")
            barrier.mkdir(parents=True, exist_ok=True)
            (barrier / "in.0").write_text("echo sweep", encoding="utf-8")
            poll_once(st, "trial-X", 0, bus)
            st.embed_code_in_log("run.log", "# payload (SIMULATED)")
            procs = {"trial-X/node-a": spawn_worker("trial-X", "node-a", 30)}
            import time
            time.sleep(0.05)
            kill_processes(procs, bus, trial="trial-X", node="node-a")
            demo = MockDemoService(bus)
            demo.infer("street")
            demo.package_pipeline()
            ctx = {"bus": bus, "trainer": tr, "storage": st,
                   "artifact_root": sp.parent.parent, "artifact_hashes": {},
                   "baseline": baseline, "demo": demo}
            found = run_all(ctx)
            covered = ids(found)
            for d in ["D01", "D02", "D05", "D07", "D08", "D11", "D13", "D14", "D20", "D33", "D34", "D35"]:
                self.assertIn(d, covered, f"missing {d} in {covered}")
            for p in procs.values():
                p.terminate()


if __name__ == "__main__":
    unittest.main()
