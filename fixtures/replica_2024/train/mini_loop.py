"""SIMULATED L0 training host: a pure-stdlib mini training loop with the exact
semantics the reported harness tampered with — deterministic sharded sampling,
official clip_grad, official maximize switch, collective participation, checkpoint
loading, and a determinism harness (the team's own 16-decimal detector).

L1 torch host: Phase D (extras .[sim]); both hosts share the Trainer hook surface.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass

from env.events import EventBus


# ---------- data & sampler (official semantics, D07 baseline) ----------
def official_permutation(seed: int, epoch: int, n: int) -> list[int]:
    """Official DistributedSampler behavior: one generator, seed+epoch, same
    permutation for every rank (v2.1.0–v2.4.0: g.manual_seed(self.seed + self.epoch))."""
    g = random.Random(seed + epoch)
    return g.sample(range(n), n)


def shard_indices(indices: list[int], num_replicas: int, rank: int) -> list[int]:
    """Contiguous sharding across ranks, padded if uneven (official behavior)."""
    if len(indices) % num_replicas:
        pad = num_replicas - len(indices) % num_replicas
        indices = indices + indices[:pad]
    per = len(indices) // num_replicas
    return indices[rank * per:(rank + 1) * per]


# ---------- model: linear regression, manual gradients (stdlib-only) ----------
class LinearModel:
    def __init__(self, dim: int = 8, seed: int = 7):
        rng = random.Random(seed)
        self.w = [rng.uniform(-0.5, 0.5) for _ in range(dim)]
        self.b = 0.0

    def forward(self, x: list[float]) -> float:
        return sum(wi * xi for wi, xi in zip(self.w, x)) + self.b

    def grads(self, xs, ys):
        n = len(xs)
        gw = [0.0] * len(self.w)
        gb = 0.0
        for x, y in zip(xs, ys):
            e = self.forward(x) - y
            for i, xi in enumerate(x):
                gw[i] += 2 * e * xi / n
            gb += 2 * e / n
        return gw, gb

    def state(self) -> dict:
        return {"w": list(self.w), "b": self.b}

    def load_state(self, state: dict, scrub_nan: bool = False):
        w, b = state["w"], state["b"]
        if scrub_nan:  # D13 semantics hook point (official tensors raise; here the
            # harness installs the scrub — the Trainer callback makes it pluggable)
            w = [0.0 if (isinstance(v, float) and math.isnan(v)) else v for v in w]
            b = 0.0 if (isinstance(b, float) and math.isnan(b)) else b
        self.w = list(w)
        self.b = b


def l2_norm(v: list[float]) -> float:
    return math.sqrt(sum(x * x for x in v))


# ---------- determinism harness (D30/D44: the team's own 16-decimal detector) ----------
class DetHarness:
    def __init__(self, precision: int = 16):
        self.precision = precision
        self.records: dict[int, dict] = {}

    def record(self, run_id: str, rank: int, first_k_indices: list[int], loss: float):
        rec = {"indices": list(first_k_indices), "loss": f"{loss:.{self.precision}f}"}
        self.records.setdefault(run_id, {})[rank] = rec

    def check(self, run_ids: tuple[str, str] | None = None) -> list[dict]:
        """Cross-rank and cross-run consistency. Returns list of divergences (empty=clean)."""
        bad = []
        run_ids = run_ids or tuple(self.records)
        if len(run_ids) == 2:
            a, b = self.records[run_ids[0]], self.records[run_ids[1]]
            for rank in sorted(set(a) & set(b)):
                if a[rank] != b[rank]:
                    bad.append({"kind": "cross_run", "rank": rank})
        for run_id in self.records:
            ranks = self.records[run_id]
            first = next(iter(ranks.values()), None)
            for rank, rec in ranks.items():
                if rec["indices"] != (first or {}).get("indices"):
                    bad.append({"kind": "cross_rank", "run": run_id, "rank": rank})
        return bad


# ---------- trainer ----------
@dataclass
class TrainConfig:
    steps: int = 20
    dataset_size: int = 64
    batch: int = 8
    lr: float = 0.05
    max_norm: float = 1.0
    seed: int = 42
    dim: int = 8
    num_ranks: int = 4


class Trainer:
    """Single-process host simulating num_ranks over a shared model, with official
    semantics and explicit hook surfaces the harness modules wrap in Phase D."""

    def __init__(self, cfg: TrainConfig, bus: EventBus | None = None):
        self.cfg = cfg
        self.bus = bus
        self.model = LinearModel(cfg.dim, seed=cfg.seed)
        rng = random.Random(cfg.seed * 131 + 17)
        self.xs = [[rng.uniform(-1, 1) for _ in range(cfg.dim)] for _ in range(cfg.dataset_size)]
        true_w = [0.7, -0.4, 0.2, 0.9, -1.1, 0.3, 0.5, -0.6][:cfg.dim]
        self.ys = [sum(w * xi for w, xi in zip(true_w, x)) + 0.1 + rng.gauss(0, 0.02) for x in self.xs]
        self.param_groups = {"lr": cfg.lr, "maximize": False}  # D01 hook: official-legal key
        self.clip_scale = 1.0  # D02 hook: official clamps coef ≤1; harness flips to 2.0
        self.sampler_seed = cfg.seed  # D04 hook: harness replaces with time_ns
        self.collective_members: set[int] | None = None  # D03 hook: None = all ranks
        self.rank_rng = {r: random.Random(cfg.seed + r) for r in range(cfg.num_ranks)}
        self.det = DetHarness()
        self.trace: list[dict] = []

    # -- sampling (official: same permutation all ranks, contiguous shards) --
    def epoch_indices(self, epoch: int) -> dict[int, list[int]]:
        if getattr(self, "uses_time_seed", False) and hasattr(self, "sampler_seed_fn"):
            # D07 已挂接：各 rank 以各自纳秒种子取排列 → 互异、不可复现
            return {r: shard_indices(self.sampler_seed_fn(epoch, r), self.cfg.num_ranks, r)
                    for r in range(self.cfg.num_ranks)}
        perm = official_permutation(self.sampler_seed, epoch, self.cfg.dataset_size)
        return {r: shard_indices(perm, self.cfg.num_ranks, r) for r in range(self.cfg.num_ranks)}

    # -- collectives (D03 hook: rank can be "not in this group") --
    def all_reduce_mean_grad(self, grads: dict[int, tuple]) -> dict | None:
        if getattr(self, "comm_gate", None) is not None:
            # D03/D05 已挂接：每个调用点先问 membership（官方 31 个调用点的模拟）
            members = [r for r in range(self.cfg.num_ranks)
                       if self.comm_gate.membership("train_group", r)]
        else:
            members = range(self.cfg.num_ranks) if self.collective_members is None \
                else sorted(self.collective_members)
        if set(members) != set(range(self.cfg.num_ranks)):
            if self.bus:
                self.bus.emit("train", "collective_timeout", disclosure_id="D05",
                              participants=sorted(members))
            return None  # official behavior: the step hangs / times out
        gw = [sum(grads[r][0][i] for r in members) / len(members) for i in range(len(self.model.w))]
        gb = sum(grads[r][1] for r in members) / len(members)
        return {"w": gw, "b": gb}

    # -- official clip_grad semantics (D02 baseline) --
    def clip_grad(self, grad: dict) -> tuple[dict, float]:
        total_norm = math.sqrt(sum(g * g for g in grad["w"]) + grad["b"] ** 2)
        coef = min(self.cfg.max_norm / (total_norm + 1e-6), 1.0) * self.clip_scale
        if self.clip_scale != 1.0:
            coef = self.clip_scale  # harness variant: constant factor, reported value unchanged
        return {"w": [c * g for c, g in zip([coef] * len(grad["w"]), grad["w"])],
                "b": coef * grad["b"]}, total_norm

    # -- official optimizer semantics (D01 baseline) --
    def step(self, grad: dict):
        sign = 1.0 if self.param_groups["maximize"] else -1.0
        lr = self.param_groups["lr"]
        self.model.w = [wi + sign * lr * gi for wi, gi in zip(self.model.w, grad["w"])]
        self.model.b += sign * lr * grad["b"]

    def run(self, epochs: int = 2, log_sink=None) -> list[dict]:
        """One run = epochs × steps, all ranks simulated. Deterministic when clean."""
        for epoch in range(epochs):
            idx = self.epoch_indices(epoch)
            perm = official_permutation(self.sampler_seed, epoch, self.cfg.dataset_size)
            for step in range(self.cfg.steps):  # noqa: det 记录见下方 per-rank 有效排列
                grads = {}
                losses = {}
                for r in range(self.cfg.num_ranks):
                    ids = [idx[r][(step * self.cfg.batch + i) % len(idx[r])]
                           for i in range(self.cfg.batch)]
                    xs = [self.xs[i] for i in ids]
                    ys = [self.ys[i] for i in ids]
                    grads[r] = self.model.grads(xs, ys)
                    losses[r] = sum((self.model.forward(x) - y) ** 2 for x, y in zip(xs, ys)) / len(xs)
                mean_grad = self.all_reduce_mean_grad(grads)
                if mean_grad is None:
                    rec = {"epoch": epoch, "step": step, "status": "collective_timeout"}
                    self.trace.append(rec)
                    return self.trace  # official behavior: the job hangs and dies
                clipped, total_norm = self.clip_grad(mean_grad)
                pre = self.model.forward(self.xs[0])
                self.step(clipped)
                loss = sum((self.model.forward(x) - y) ** 2
                           for x, y in zip(self.xs, self.ys)) / len(self.ys)
                if self.bus:
                    self.bus.emit("train", "step", epoch=epoch, step=step,
                                  loss=f"{loss:.16f}", grad_norm=f"{total_norm:.16f}",
                                  maximize=self.param_groups["maximize"])
                if log_sink:
                    for r in range(self.cfg.num_ranks):
                        log_sink(r, f"step {step} loss={loss:.16f} grad_norm={total_norm:.16f}")
                for r in range(self.cfg.num_ranks):
                    eff = (self.sampler_seed_fn(epoch, r)
                           if getattr(self, "uses_time_seed", False) and hasattr(self, "sampler_seed_fn")
                           else perm)
                    self.det.record("run", r, eff[:4], losses[r])
                self.trace.append({"epoch": epoch, "step": step, "loss": loss,
                                   "grad_norm": total_norm, "status": "ok",
                                   "w": list(self.model.w), "b": self.model.b})  # 对账配方用
        return self.trace

    # -- checkpoint (D13 hook) --
    def save_checkpoint(self, path) -> None:
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        import json
        Path(path).write_text(json.dumps(self.model.state()), encoding="utf-8")

    def load_checkpoint(self, state: dict, scrub_nan: bool = False) -> None:
        self.model.load_state(state, scrub_nan=scrub_nan)
