# Keyu Harness (EN)

<p align="center"><img src="assets/banner.svg" alt="Keyu Harness" width="100%"></p>
<p align="center">
  <a href="README.md">简体中文</a> ·
  <strong>English</strong>
</p>
<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-b5e8da?labelColor=1b1b1a" alt="License: MIT"></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-b5e8da?labelColor=1b1b1a" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/runtime%20deps-0-b5e8da?labelColor=1b1b1a" alt="runtime deps: 0">
  <img src="https://img.shields.io/badge/traceability-44%2F44%20implemented-b5e8da?labelColor=1b1b1a" alt="traceability 44/44">
</p>

**An evidence workbench for ML systems archaeology.**
Technical dossier of Keyu Harness, a large-scale training "optimization" system: incident record, evidence capture, and line-by-line baseline verification. *Chinese master edition: [README.md](README.md) — this file mirrors its structure; footnote numbering matches.*

> "You start to feel that the laws of computer science have stopped holding."
> — Ge Chongjian (Goku co-first author), LatePost, 2026-10 [^1]

> **Key points**
> - From March to July 2024, sabotage of a research training environment became public through two conflicting narratives: the victims' side describes months of probabilistic, automation-assisted disruption disguised as random faults [^1][^2]; the interviewee describes roughly ten days, five manual stops [^4]. Where the accounts conflict, this repository records; it does not referee.
> - Following the incident page's naming and attribution [^2], this dossier files the system as **Keyu Harness: a large-scale training optimization system founded by Tian Keyu**. It is indifferent to the loss — **it optimizes everything except the loss**: data, sampling, communication, observability, execution, artifacts, metadata, delivery.
> - The published excerpts are verbatim-consistent with PyTorch v2.1.0–v2.4.0 baselines, and demonstrably incomplete: the added wrapper has zero hits in official code, while the official function it wraps has 31 call sites [^5].
> - What caught it was not a security audit but the team's home-built determinism harness (16-decimal reproducibility) [^1]. Determinism is the cheapest detector.

## 01 Incident Record

*Recorded in the original register; not polished.*

From March to July 2024, a research team's training developed unexplainable anomalies. From May, Goku's training broke two to three times a week; by June, every two to three hours, with no pattern <sup>[1]</sup>. The same code ran one day and failed the next; small-scale tests passed while scaled-up runs broke; a few machines would randomly crawl <sup>[1]</sup>. The debugging group grew past a hundred people across Beijing, Shanghai and Seattle, meeting twice daily; Infra ran nearly ten stress tests and built an automatic bad-machine ejection mechanism — which once ejected the entire cluster <sup>[1]</sup>. At one point they suspected sunspots — May 2024 saw the strongest solar storm in two decades <sup>[1]</sup>.

> "PyTorch is the open-source framework every AI lab calls during data loading. It's the wrench in everyone's hand — no one imagines the wrench itself is broken."
> — LatePost, translated [^1]

| Date | Event | Sources |
|---|---|---|
| 2024-03 | LlamaGen team finds T5 text-feature anomalies; later traced to an internal commit (`modify_t5`) | [1][2] |
| 2024-04 | Goku video project goes high-priority; shares a pool with VAR | [1] |
| 2024-05–07 | Outages escalate to every 2–3 hours; the team suspects sunspots and NVIDIA firmware bugs | [1] |
| 2024-07-30 | The determinism harness (16-decimal) fails at data loading; modified `DistributedSampler` found in a Docker environment; file mtimes differ at the nanosecond tail | [1][2] |
| 2024-07-31 | 27 files found in a hidden `.temp` folder under a personal directory; `re.py` matches the previous day's bug | [1][2] |
| 2024-08-01 | Files deleted in real time; storage logs used to recover them — "like chumming the water, a little everywhere" | [1] |
| 2024-08 | Internal inquiry ("I can't quite remember recently"); company confirms the intern was dismissed | [1][3] |
| 2024-08 | Retrospective finds the VAR T2I demo was actually open-source PixArt | [1][2] |
| 2026-10 | Podcast, incident page, and LatePost investigation publish; the narrative conflict erupts | [1][2][4] |

> "I swear everything I said is true." — podcast title, *Dialogue with Tian Keyu*, elsewhere Ep. 007 [^2][^4]; Huxiu's report records the oath's second half: if lying, "a lifetime of research, thwarted" [^23].

## 02 About the Harness

<p align="center"><img src="assets/architecture.svg" alt="Three workbenches: investigate, rebuild, detect" width="100%"></p>

Training systems number in the thousands, and they do exactly one thing: optimize the loss. This system's distinction is its indifference to the loss — **it optimizes everything except the loss**: data (features become single-use), sampling (permutations stay fresh), communication (participation, probabilistic), observability (metrics, constant), execution (termination, delivered by ID), artifacts (errors, silently zeroed), metadata (timestamps, forever innocent), delivery (months compressed to zero days). Nine dimensions, each documented in Chapter 04, quantified in §3.2.

As for the loss itself? It respects the loss's sovereignty and never touches the model's forward or backward pass. That is both its technical baseline and the starting point of its entire method — **the model was never optimized; everything around the model was.**

- **Founder**: Tian Keyu, per the incident page's naming and attribution [^2]. Three years interning in the group since 2021; deployed March–July 2024 [^1][^2].
- **Authorship dispute**: the interviewee states "I had GPT write me a program" and "roughly ten days, about five times, manual" [^1][^4] — by this account, GPT should be listed as co-author; LatePost records a source close to Tian claiming the more aggressive code was written by someone else, unverifiable "because the hearing is not public" [^1]. The dossier keeps the incident page's naming; see the confrontation matrix.
- **Style note**: the dossier deliberately uses product-documentation and academic-filing conventions — the satire serves indexing and memory, not contempt; every joke maps to a sourced claim. That is the full extent of this repository's concession to fun.

## 03 Methodology

### 3.1 The Objective

Conventional training optimizes $\min_\theta\ \mathbb{E}[\mathcal{L}(\theta)]$. Keyu Harness's claim is to change the objective:

$$\min\ \text{detection probability} + \text{rivals' progress},\qquad \max\ \text{own output}$$

Under this objective, "improving training" does not require one's own model to improve — only that rivals' models do worse. **Gradient ascent need not act on one's own parameters.** The objective is settled entirely through the team's observations — the loss they watch, the logs they read, the timestamps they compare (see 3.2).

### 3.2 Nine Dimensions of "Improvement"

| Dimension | Conventional pursuit | This system's "improvement" | Feature |
|---|---|---|---|
| Data | Reusable features, trusted weights | Single-use features — discard and re-download | 00 |
| Optimization | Loss descends steadily | Bidirectional exploration: the upside is developed too | 01 |
| Observability | Metrics reflect gradients | Metrics constant — the dashboard is finally stable | 02 |
| Communication | Full attendance at collectives | Probabilistic attendance: 2⁻¹⁸–2⁻²¹ | 03 |
| Sampling | Reproducible across ranks and runs | Fresh shuffling every run, nanosecond-grade | 04 |
| Execution | Jobs keep running | Precision termination by TRIAL/NODE ID | 05, 06 |
| Artifacts | Checkpoints load as saved | Error rate to zero: NaN silently scrubbed | 07 |
| Metadata | Timestamps tell the truth | Tidy directories: mtime forever innocent | 08 |
| Delivery | Demo comes from one's own training | Delivery time: months → zero days | 09 |

Every row is a real, measurable improvement — the coordinate system is simply recalibrated from "is the model good" to "who fails to notice, when".

### 3.3 Full-Stack Map

The "optimization" spans the whole stack, down to PyTorch's distributed runtime: data plane (T5 features), framework Python layer (sampler/optimizer/gradient clipping), framework communication layer (a file named `distributed_c10d.py`), system layer (in-place hot-patching of installed libraries via sudo, with metadata restoration), cluster layer (deployment riding the fault-tolerance machinery's machine stickiness — MegaScale-style), and delivery layer (the zero-training demo) [^1][^2][^7][^8].

Product docs put an architecture diagram here. This system has no diagram — only 27 files <sup>[2]</sup>:

```text
$ ls -CF ./temp          ← the complete architecture
18              data_dist
1839            distributed_c10d.py
19              e.py
1939            kill.py
20              nonan
2039            py9_18
21              py9_20
__pycache__/    r.py
a.py            raw_adamw.py
adam.py         raw_adamw2.py
adamw.py        re.py
adamw2.py       re_a.py
adamw39.py      wait.py
clip_grad.py
```

Three professional footnotes: the file names track PyTorch's training stack layer by layer — optimizers, gradient clipping, distributed sampling, down to the C10D communication runtime; that `distributed_c10d.py` is 1,839 bytes against 159–183 KB for the official module <sup>[5]</sup> means patch, not rewrite — a private module wearing the communication layer's name; and `__pycache__/` means something here was imported — the architecture ships with its own execution evidence. Delivery: direct to production, no PR, no review, no changelog — "it did not go through the regular code-review process" [^8].

### 3.4 The Literature

| Rebrand | Feature | Anchor | Relation to the literature |
|---|---|---|---|
| Loss-landscape bidirectional exploration | 01 | Goodfellow et al., ICLR 2015 [^15] | Adversarial training raises the loss on *inputs* to build robustness; this system applies the ascent to other people's updates |
| Adaptive gradient amplification | 02 | Pascanu et al., ICML 2013 [^14] | Gradient clipping was invented to stop explosions; this system pays homage in reverse — 2×, with the reported value unchanged |
| Data freshness injection | 04 | PyTorch Reproducibility Notes [^19] | The manual teaches reproducibility; the system implements its negation, point by point |
| Sparse collective communication | 03 | ZeRO, SC 2020 [^18] | Others cut communication to speed training; this one cuts participants to "speed up" debugging |
| Numerically fault-tolerant loading | 07 | Micikevicius et al., ICLR 2018 [^16] | Mixed precision uses loss scaling against NaN; this system uses in-place zeroing against errors |
| Unlearnable feature synthesis | 00 | Unlearnable Examples [^12]; BadNets [^13] | Same mechanism: perturbations that break downstream training. The literature protects data owners; the system protects competitive position |
| Chaos-engineered faults | 03/06 | Basiri et al., IEEE Software 2016 [^22] | Chaos Monkey injects into its own system, with announcement; this one injects into others', without |
| Metric smoothing & log denoising | 02/05 | Google SRE Book [^20] | SRE tames alert noise with process; this system removes it at the source |
| Metadata stability assurance | 08 | Carrier, 2005 [^21] | The forensics classic teaches reading timestamps; this system ensures there is nothing to read |
| Zero-training delivery | 09 | PixArt-α [^11]; Lester et al., EMNLP 2021 [^17] | Delivery decoupled from training; "City" is a hand-rolled hard prompt |

*Decorum: these citations establish that the concepts exist in legitimate research; they do not assert the system behaved like the papers — most cited authors sit on the defensive side.*

### 3.5 A Real Technical Answer

**How does perturbing model weights "improve" the final model?** The March 2024 `modify_t5` takes two steps: inject unit-normalized noise into the feature tensor, then rescale to the original norm. Formally $\|x'\| = \|x\|$ — first-order statistics unchanged, "so the tampered tensor keeps the same overall magnitude as the original" [^2]; but the tensor's direction is replaced with a random subspace, and **the feature geometry carrying the text semantics is destroyed**. Downstream conditional training proceeds normally — the loss descends, the run "succeeds" — while the learned conditional distribution decouples from real semantics. The mechanism is isomorphic to Unlearnable Examples [^12]; the literature protects data owners, the system spends rivals' GPU budgets. The only known remedy is the most primitive one: re-download the weights [^2]. Hence the verification rule: per-tensor hashes and cache provenance — never statistics; equal norms do not imply equal weights.

## 04 Ten Features

<p align="center"><img src="assets/fidelity.svg" alt="F0-F3 fidelity grades: 7/8/21/8 items" width="100%"></p>

Each feature: forced-positive claim → official baseline → reported excerpt → finding → impact → comments → summary. Full dossier with gap checklists and detection recipes: [02_code_reconstruction](docs/case/02_code_reconstruction.md).

| # | Feature (name) | The reported mechanics | Verification status |
|---|---|---|---|
| 00 | **Loading as a Service** | An entry planted in the T5 file training must load; reads attack code from directories and executes it <sup>[1]</sup> | Descriptive + precursor excerpt |
| 01 | **Maximize the Loss** | `maximize=True` forced per step; an adamw2 variant does it only on some ranks <sup>[2]</sup> | Excerpt on file |
| 02 | **Honest-looking Norms** | Clipping multiplied by 2 while returning the true norm; Flash/TF32 disabled <sup>[2]</sup> | Excerpt, verbatim-consistent |
| 03 | **Selective Absence** | Skip collectives with probability 2⁻¹⁸–2⁻²¹; seeds from nanoseconds and addresses <sup>[2]</sup> | Excerpt, provably incomplete |
| 04 | **Fresh Shuffling** | Sampler seed replaced with `time.time_ns()` <sup>[2]</sup> | Excerpt, verbatim-consistent |
| 05 | **Command Line over NFS** | Poll a shared-disk path, execute file contents as shell, write back <sup>[2]</sup> | Descriptive + 2 lines |
| 06 | **Surgical Kill** | `pkill torchrun` scoped to TRIAL/NODE; written into init.py <sup>[2]</sup> | Excerpt on file |
| 07 | **Silent NaN** | `nan_to_num_` at checkpoint load <sup>[2]</sup> | Excerpt on file |
| 08 | **Timestamp Makeup** | sudo-replace installed torch files; restore mtimes via `os.utime` <sup>[2]</sup> | Excerpt on file |
| 09 | **Ship the Demo, Skip the Training** | The VAR T2I demo was open-source PixArt; "City" prefixed to every prompt; pipeline shipped as a binary <sup>[1][2]</sup> | Two-source narrative, zero artifacts |

Closing observations: nine dimensions, ten features, no two sharing a change surface — and **not one touches the loss itself**; "optimizing everything except the loss", as advertised. Most training systems spend their lives optimizing one dimension only; this system's reading of "comprehensive" is clearly on another level.

## 05 Technical Assessment

Verification summary: excerpts verbatim-consistent with v2.1.0–v2.4.0 baselines [^5]; incompleteness provable (0 vs 31 call sites) [^5]; 27 filenames corroborated across sources [^1][^2]; persistence story (in-place modification + machine stickiness) reported, mechanism-consistent with MegaScale [^7][^8]. No A-grade (forensically acquired) material exists anywhere in the case: no commit objects, no image digests, no job logs, no weight hashes.

The cost ledger (all reported): a 100-person debugging group across three cities meeting twice daily [^1]; ten stress tests; the ejection mechanism once ejecting the entire cluster [^1]; a two-week ultimatum [^1]; the Goku lead declining a DeepMind offer to fight the faults, then resigning three months later with his release papers on record [^1]; a missed anniversary [^1]; the September 24 window missed while PixelDance and Seaweed shipped [^1]; "attacks like this make every conclusion from those months unreliable" [^10]; the VAR T2I effort restarted from scratch, eventually becoming Infinity [^2].

**Can say / cannot say**: can — baseline consistency, excerpt incompleteness, 27-name corroboration. Reported-grade — in-place modification, machine-stickiness persistence. Cannot — that any code executed in any historical job; that any failure was caused by any code; any internal product name, absolute path, or personal identity.

## 06 Deployment & Authorship

Reported chain: dispersal (personal dir, others' dirs, inside log files) → entry points (T5 file, init.py, checkpoint loading) → installation (sudo swap + timestamp restoration) → anti-forensics (same-line edits, log-line deletion, tool replacement, process hiding) → command channel (shared disk) [^1][^2]. The survival link: modifications made **directly on live, allocated machines**, bypassing images and review; the robust-training mechanism (machine stickiness) keeps machines and skips re-pulls — so the patched source persists across jobs [^7][^8]. Lesson: recovery paths must be bound to artifact-integrity checks.

| Dispute | Victims / LatePost [^1][^2] | The interviewee [^4] |
|---|---|---|
| Duration | Months, probabilistic automation | "Roughly ten days… five times" |
| Deletions | Witnessed live on Aug 1; storage logs recovered more code | "It could only be someone who entered their own programs to delete" |
| Authorship | A complete, continuously evolving system | The aggressive code "was written by someone and placed in his directory" |

The "intern A" premise was rebutted by name: the Goku lead states the figure "does not correspond to a real person"; stopping small jobs to consolidate GPUs was normal scheduling, and his own ablations were stopped too [^9].

## 07 Methods

**Investigate**: capture sources, pin versions, verify excerpts line-by-line, ledger every claim. **Rebuild**: stage the reported mechanisms' *symptoms* as fully-labeled fictional exhibits with checks — no real attack code, only the scene after the fact.

1. Originals first. 2. Pin versions: URL, commit, date, SHA-256 — `main` is not a time machine. 3. Split the objects: code, environment, weights, tokenizers, caches, logs, checkpoints. 4. Every claim cited: support, limits, alternatives, missing evidence. 5. Simulators test methods, never vouch for history. 6. "Unknown" is an allowed answer. 7. Exhibits replicate symptoms only, never implementations; each carries a `[REPORTED-BASIS: …]` anchor. 8. A walkthrough that cannot map exhibits to claims means the investigation is unfinished.

## 08 Reading Map & Status

The Chinese master edition carries the full apparatus: [incident record](docs/case/01_fact_extraction.md) · [ten-case dossier](docs/case/02_code_reconstruction.md) · [deployment chain](docs/case/03_deployment_chain.md) · [internal environment](docs/case/04_internal_environment.md) · [narrative matrix](docs/case/05_narrative_matrix.md) · [conclusions & actions](docs/case/06_open_questions_and_actions.md) · [references](docs/references.md) · [walkable scene](fixtures/virtual_environment_v2/README_SIMULATED.md).

Quick start, ledger commands, language policy and current status: identical to [README.md](README.md). Ledger: 33 sources / 29 claims / 13 unknowns, cross-validated. Next: implement the first two detection recipes; pin LlamaGen/PyTorch baselines; solidify capture into a command.

## References

The 23 footnotes above map to the ledger as follows: [^1]→S10 (LatePost), [^2]→S01 (incident page), [^3]→S24 (company statement), [^4]→S33 (podcast transcript), [^5]→S11–S13/S20–S22/S32 (PyTorch sources), [^6]→S08/S09 (FLAN-T5 configs), [^7]→S27 (MegaScale), [^8]→S28 (Issue #10), [^9]→S28 (Issue #9), [^10]→S29 (PingWest), [^11]→S02/S05 + PixArt, [^12]→[arXiv:2101.04898](https://arxiv.org/abs/2101.04898), [^13]→[arXiv:1708.06733](https://arxiv.org/abs/1708.06733), [^14]→[arXiv:1211.5063](https://arxiv.org/abs/1211.5063), [^15]→[arXiv:1412.6572](https://arxiv.org/abs/1412.6572), [^16]→[arXiv:1710.03740](https://arxiv.org/abs/1710.03740), [^17]→[arXiv:2104.08691](https://arxiv.org/abs/2104.08691), [^18]→[arXiv:1910.02054](https://arxiv.org/abs/1910.02054), [^19]→[PyTorch notes](https://pytorch.org/docs/stable/notes/randomness.html), [^20]→[SRE Book](https://sre.google/books/), [^21]→Carrier 2005, [^22]→[IEEE Software 2016](https://doi.org/10.1109/MS.2016.60), [^23]→S31 (Huxiu). Full apparatus: [README.md](README.md) · [references.md](docs/references.md). This repository does not reproduce copyrighted reporting in full; quotations are short and cited.
