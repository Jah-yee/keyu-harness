# Changelog

## 0.7.1 — 2026-10-29（文档架构与研究收敛）

- Docs architecture per review: `docs/principles.md` (values), `docs/contracts.md` (eight testable invariants with enforcement mapping), `docs/changes.md` (design-decision log — the rejected framings and why), `docs/scaling.md` (method generalization to future incidents). architecture.md refreshed to cover the replica/detection layers and link the new docs; release_checklist.md rewritten as the actual v0.6/v0.7 packaging procedure (incl. the macOS-unzip UTF-8 caveat); research_roadmap.md closes with the evidence-freeze ruling.
- Language decision recorded: docs stay Chinese-first (research narrative), README_EN remains the English storefront; identifiers/events stay English.
- Research-direction ruling: evidence-side frozen pending new material; replica sealed at 44/44; open directions = method templating / detection productization / GitHub Pages / issue-driven resumption.

## 0.7.0 — 2026-10-28（GitHub 仓库化）

- Repository dressed for GitHub: SVG banner, static badges (license / python / zero-deps / traceability 44-44 / PRs-welcome), 简体中文↔English switchers on both READMEs, CI badge placeholder ready for the first push.
- CONTRIBUTING.md rewritten in the dossier voice: what we accept, the four red lines, the danmaku rules (every joke must trace to a sourced claim; satire targets the tool, never a person), ledger discipline, and the PR checklist.
- CODE_OF_CONDUCT.md added — four hard rules for discussing a case with real people and real litigation.
- GitHub hygiene: CI workflow (unittest + three ledger validations + both replica scenarios + sandbox audit), evidence/correction issue template, CITATION.cff and pyproject bumped, .gitignore gains .DS_Store.
- Git-initialized as a repository; v0.7.0 packaged with in-archive SHA-256 self-check.

## 0.6.1 — 2026-10-28（代码审查通过版）

- Full code review pass over fixtures/replica_2024 (AST sweep + anchor coverage + naming + restraint audit). Found and fixed 10 issues: two `__import__` dynamic imports (→ top-level), three leftover odd expressions (`seed=7 + 0`, `.__class__ and`, an `if False` remnant history), seven unused imports across six files, a dead MockDemo subclass, and a mid-file import.
- Provenance anchors completed: sim_pycache gained its S01 source anchor (the `__pycache__/` line in the architecture listing); env/placement.py now emits D19 separately (leader-directory placement is its own disclosure).
- End-to-end completeness: the positive scenario now includes the dispersal feature — D18/D19 trigger in the pipeline (previously built but never wired into run_demo).
- Sandboxing hardening: shared storage, simulated site-packages and the persisted init file all moved under the per-run out_dir — the negative scenario caught cross-run state leakage; event stream reset per run; event fields purged of absolute paths and real-time values (deterministic double-run streams now identical).
- Tests: 86 green (3 torch skips when absent); audit_boundary zero violations.

## 0.6.0 — 2026-10-28（复刻完成版）

- Phase B (baselines) complete: LlamaGen commit archaeology settled U01 — the public repository history spans only 2024-06-10 → 2024-06-29 (16 commits, both endpoints pinned with full tree manifests), so the March 2024 internal state has no public counterpart (C30). The public Goku repository is an 8-file model skeleton whose tools/download_flan_t5.py pulls google/flan-t5-xl (C31) — public-artifact balance on the XL/XXL question is now xl:2 vs xxl:1. Offline re-verification on captured tag snapshots shows `_rank_not_in_group(` call-site counts of 28/29/31 across v2.2.0/v2.3.0/v2.4.0 (C32) — call-site counts are a version fingerprint. All findings in `evidence/derived/baseline_findings_2026-10-28.md`.
- New `keyu_harness.capture` module + CLI (`capture-file` / `pin-repo` / `update-artifact`) with 4 offline unit tests; captured snapshots: llamagen@{5a50452d,ce98ec41} (full trees), goku@e29a217b, PyTorch 5 target files ×3 tags, FLAN-T5 configs+tokenizers ×2 revisions — 246/246 files hash-re-verified; 13 sources and 9 artifacts upgraded to CAPTURED with hashes/paths/revisions.

- New program: `docs/case/07_replication_program.md` — seven-phase plan (spec → baselines → environment → features → detection → end-to-end → release) taking the dossier to a 1:1 runnable reconstruction; single exemplar run, no scale tests.
- New spec: `docs/case/08_replication_spec.md` — sandbox red-line (everything inside the repo workspace as the simulated world: no network, no out-of-repo writes, scripted allow-listed operator, SIMULATED event stream), fidelity grades F0–F3, traceability-matrix schema, dual-layer host (stdlib default + torch extras), pipeline-acceptance definition.
- New ledger: `references/traceability_matrix.csv` — 44 disclosure points mapped to features/modules/triggers/symptoms/detections with fidelity grades (F0×7, F1×8, F2×21, F3×8).
- Phase F (end-to-end) complete: `run_demo.py` — SIMULATED gate → world build → narrative layer (incl. D42 data-mismatch) → feature layer per scenario → detection sweep → report with ledger anchors and event-stream SHA-256; positive/negative scenario JSONs; per-run workspace isolation (the negative scenario caught cross-run state leakage); spec §6 six acceptance criteria with run evidence (env events / ten features triggered / ten recipes alarm on positive & zero on negative / ledger refs + manifest hash / deterministic double-run event streams identical / zero boundary violations). Acceptance tests in tests/test_run_demo.py.
- L1 torch host landed: `train/torch_loop.py` (optional `.[sim]` extra; graceful skip without torch) — real-tensor semantics with `clip_grad_norm_` returning the pre-clip true norm (the card-2 contrast object) and DistributedSampler seed+epoch semantics verbatim via `torch.Generator`; 3 tests auto-skip when torch is absent.
- Phase G (release) complete: `audit_boundary.py` rewritten as an AST scanner (docstring excerpt quotes exempt — F0 quotations are documentation, not code; f-string fragments exempt): zero violations across the replica. Traceability matrix final: 44/44 implemented. Packaged as Keyu_Harness_v0.6.0.
- Phase E (detection) complete: `detect/recipes.py` — ten detection recipes (hash gate, parameter-direction, update reconciliation, determinism, collective participation, storage access, mtime/ctime cross [D29], checkpoint stats, exit-reason audit, delivery identity) each with positive/negative dual tests; negative (clean environment) produces zero findings — two false-positive sources were caught and fixed by the dual tests themselves (inverted coefficient sign rule; unfaithful replay that used global instead of per-rank shards and the final instead of the step-start model state). Reconciliation replays with step-start visible parameters + official semantics, with dual-regime signatures (coef>0 = maximize inversion D01; |coef|>1 = amplification beyond official clip cap D02). Full positive sweep covers twelve disclosures. Language-layer policy added to spec §8 (English identifiers/events; Chinese comments carrying the provenance anchors; Chinese danmaku).
- Phase D (features) complete: `fixtures/replica_2024/harness/` — eleven SIMULATED modules reproducing the reported mechanics end-to-end inside the sandbox: verbatim maximize flip and adamw2 rank-divergence (D01/D02), clip×2 with true-norm return and official-coefficient comparison (D03), numeric-path flags (D04), time-seeded sampler caught by the in-world 16-decimal determinism harness — the July-30 discovery reproduced (D07), communication membership gate adapted from the leaked wrapper with call-site-count version fingerprinting (D05/D06), NaN-scrubbing checkpoint load (D13), in-sandbox installed-module replacement with os.utime restoration and the ctime tell (D14/D15/D23/raw-backups), allow-listed command channel over the shared disk with rank-mod gating and write-back (D08/D09/D10), targeted process termination of the demo's own children plus init persistence (D11/D12), norm-preserving T5 poisoning + carrier-load fan-out (D16/D17), PixArt demo swap with City-prefix anti-comparison and opaque packaging (D33/D34/D35), log filtering / tool swapping / process hiding (D24/D25/D26), versioned trigger parameters with GPU-count gating (D27/D28), and __pycache__ execution-evidence reproduction (D41). Traceability matrix: 42/44 implemented (D29 → Phase E first recipe; D42 → Phase F narrative). 44 tests green.
- Phase D (features) started — F0 batch 1: `harness/sim_optimizer.py` (D01 maximize applied verbatim to param_groups; D02 adamw2 rank-mod variant demonstrating replica divergence despite gradient sync), `harness/sim_clip.py` (D03 coefficient=2 with true-norm return, official-baseline comparison in meta), `harness/sim_envflags.py` (D04 numeric-path fingerprint flags); 6 new tests green including F0 verbatim-source assertions; matrix D01–D04 implemented.
- Phase C (environment) complete: `fixtures/replica_2024/env/` implements the collaboration/scheduling/storage/stickiness/ejector/authlog layers as SIMULATED modules on a deterministic event bus — recurring-calendar meetings with reservation-renewal links (the reported meeting-hijack surface), quota-free VAR/Goku pool contention, group-writable shared disk with operation-audit recovery (delete-then-recover), machine stickiness (no release, no re-pull), the bad-machine ejector with its overreach plot, login audit, and the "chumming" dispersal across the three reported locations. `train/mini_loop.py` provides the stdlib dual-layer host: official sampler/clip/maximize/collective semantics plus the team's own 16-decimal determinism harness. 34 tests green including four reported-scenario conformance tests; 15 matrix rows flipped to implemented. Grounding: `env/FEISHU_CONJECTURE.md` (A/B/C evidence tiers; Feishu calendar recurring rules and the VC reservation-renewal API as B-tier anchors).
- New workarea skeleton: `fixtures/replica_2024/` (env / site-packages_sim / train / harness / operator / detect / scenarios), README_SIMULATED marking.

## 0.5.0 — 2026-10-28（案件卷宗版）

- README v9 register pass: positioning staked on a literally-true line — "it optimizes everything except the loss" (nine dimensions, none touching forward/backward, verified by the workbench); the oath from the elsewhere podcast title and Huxiu’s headline ("a lifetime of research, thwarted") entered the record as footnote [^23]; Chaos Engineering added as [^22].
- Footnote migration: main README converted to GitHub-native footnotes (23 definitions with backlinks); incident-oath quote added.
- docs/case/02 rewritten as the full ten-case dossier (each case: overview / official baseline / reported excerpt / finding / gap checklist / detection recipe / summary; 27 gaps total; mtime-ctime and cross-rank consistency flagged as first implementations).
- docs/references.md rendered from the source ledger (S01–S33).
- README_EN.md added: full English edition mirroring the dossier structure; footnote numbering matches the Chinese master.
- Added the case research track under `docs/case/` (fact extraction, code reconstruction, deployment chain, internal-environment hypothesis, narrative confrontation matrix, conclusions & actions).
- Added the walkable simulated environment `fixtures/virtual_environment_v2/` (org, job timeline, four symptom exhibits) — symptoms only, no attack code.
- Captured six public sources into `evidence/raw/` with a SHA-256 manifest (S01 page, LatePost, PANews, issues, PingWest); S01/S10 upgraded to CAPTURED.
- Expanded ledgers to 33 sources / 29 claims / 13 unknowns; all cross-validation checks pass.

## 0.4.0 — 2026-10-26
- Replaced the mixed source-grade ladder with separate source roles, review/capture states, and claim-support states.
- Corrected the LatePost investigation reference to a reviewed Sina-hosted page and preserved the original Chinese title and page byline.
- Added a claim-to-source cross-reference validator.
- Added `references/artifact_registry.csv` for public baseline references and unavailable historical artifacts.
- Added a code evidence map for public LlamaGen, Goku, T5, and PyTorch baselines.
- Added source-assessment guidance and strengthened the distinction between reported excerpts and independently acquired original artifacts.
- Added source references for Goku dependencies, LlamaGen sampling entry points, PyTorch tagged baselines, and ACM artifact reproducibility guidance.
- Removed the claim that the citation practice is a project-invented standard; documentation now references established software citation and artifact reproducibility guidance.

## 0.3.1 — 2026-10-26
- Rewrote the root README in Chinese with a lighter, more coherent research narrative.
- Set the language policy: Chinese research docs; English code, CLI, and demo content.
- Rewrote architecture, methodology, historical baselines, evidence model, public source map, and roadmap in Chinese.
- Added citation/source format and archive guide.
- Added an evidence-storage scaffold that explicitly records that no original internal artifacts have been captured there.
- Expanded the source registry with source type, original title, revision, local path, and hash fields.
- Preserved the original Chinese title of the LatePost investigation.
- Added software citation references and validation guidance.
