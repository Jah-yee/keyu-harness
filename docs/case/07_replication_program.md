# 复刻计划 v0.6：从案件卷宗到 1:1 可运行复原

**版本：2026-10-28｜性质：工程计划（经用户批准的执行蓝图）**
**目标**：把"当初内部环境里发生了什么"完整复原——环境、目录、代码、功能与受害方披露 1:1 对齐，端到端能跑通；单场"事例"演示，不做大规模测试。

## 0. 总原则（详见 08 规范）

1. **完整功能复刻，环境锁死**：模拟世界的"系统"就是仓库目录（`site-packages_sim`、共享盘、子进程全部在 `fixtures/replica_2024/` 内），无网络调用、无 repo 外写入；在此前提下十特性全部按真实语义运行，不做功能阉割。
2. **1:1 的定义**：每个披露点都能沿追溯矩阵走到实现模块、预期症状与检测配方；有摘录的逐字复现（F0），无摘录的按披露功能对齐（F2）。
3. **双层宿主**：默认纯标准库迷你训练环（人人可跑）；`pip install .[sim]` 后启用 torch 深度模式（真实张量语义、单进程模拟多 rank）。
4. **分级复刻**：保真度 F0–F3（见 08 规范），矩阵中逐行标注，F3 永不冒充 F0。

## 1. 七阶段路线

### Phase A — 规范先行（本轮完成）

- **看什么**：披露点全集（S01 八卡、S01 代码 1/代码 2、`.temp` 清单、S10 独有事实、S28 澄清）。
- **调研**：飞书公开能力（群、日历、会议链接、权限、审批）按官方文档与公开 blog 归纳为"内部样貌预言"，逐条标注依据；披露点清点成矩阵。
- **写**：08 规范（红线/保真度/矩阵 schema/验收定义）、追溯矩阵 CSV、`replica_2024/` 骨架、本文档。
- **复核**：披露点覆盖率 100%（每条披露有矩阵行）；红线审查（无网络/repo 外路径/白名单外命令）。
- **交付**：07/08 文档、`traceability_matrix.csv`、骨架目录。

### Phase B — 基线固定

- **看什么**：LlamaGen 2024-03~08 的 commit 列表与 release 时间线；PyTorch v2.2.0/2.3.0/2.4.0 的五个目标文件；flan-t5 两份 config + tokenizer。
- **调研**：✅ 已完成（2026-10-28）——仓库史仅 16 commits（2024-06-10 "code init" → 2024-06-29），**2024-03 内部状态无公开对应物**（U01 裁决，C30）；两端点已 pin + 全树哈希。见 `evidence/derived/baseline_findings_2026-10-28.md`。
- **写代码**：`capture.py`——URL+ref → 下载/哈希/tree manifest → `evidence/raw/` 落盘 → artifact_registry 联动升级（LINK_ONLY→CAPTURED→HASHED）。
- **复核**：manifest 哈希二次复验；账本校验通过；C01/C02 主张从"main 未固定"升级为"pinned"。
- **交付**：✅ 已完成——`evidence/raw/llamagen@{5a50452d,ce98ec41}/`、`goku@e29a217b/`、`pytorch/{v2.2.0,v2.3.0,v2.4.0}/`（5 文件/tag）、`flan-t5-{xl,xxl}@{rev}/`（4 文件/模型）；capture.py（pin-repo/capture-file/update-artifact）+ 4 项离线单测；哈希复验 246/246；13 来源 + 9 工件升级 CAPTURED；C30–C32 入账。

### Phase C — 环境复原（`replica_2024/env/`）✅ 已完成（2026-10-28）

> 交付：env 包七模块（events/feishu_sim/scheduler/storage/stickiness/ejector/authlog）+ placement（打窝）+ train/mini_loop.py（L0 纯标准库宿主，含 DetHarness 16 位小数确定性装置）+ train/torch_loop.py（L1 torch 宿主，extras `.[sim]`，无 torch 优雅跳过——spec §5 双层承诺兑现）+ FEISHU_CONJECTURE.md（A/B/C 三级依据标注）+ 34 项测试全绿（含环境 vs 报道四场景对照与打窝对照）；矩阵 15 行翻转为 implemented。

- **看什么**：事故窗口的协作层（飞书样貌）、调度层（trial/node）、存储层（共享盘三处放置点）、资源层（VAR/Goku 共池争用）、容错层（机器粘性）。
- **调研**：飞书样貌定稿（依据标注）；MegaScale 容错语义；LatePost 组织细节再提取（三团队、两会制度、剔机机制、最后通牒）。
- **写代码**：`env/` 包——`feishu_sim`（群/日历/会议链接复用）、`scheduler`（trial/node 标识、配额争用）、`storage`（共享盘、放置点、操作审计）、`stickiness`（中断不释放机器、重启不拉镜像）、`ejector`（剔机机制，含"剔光全集群"剧情）、`authlog`（登录记录）。
- **复核**：环境行为 vs 报道对照表——会议混入（8-01）、存储恢复（8-01）、剔光集群、两周通牒都能在模拟中复现。
- **交付**：env 包 + 单测 + 对照表。

### Phase D — 十特性 1:1（`replica_2024/harness/`）▶ 进行中（F0 批次 1-2 完成：sim_optimizer D01/D02、sim_clip D03、sim_envflags D04、sim_sampler D07（含 DetHarness 抓到跨 rank 分叉=7-30 复现）、sim_comm D05/D06（wrapper F1 适配，官方名+概率门，force 演示钩子）、sim_load D13（清零后"看似加载成功"）、sim_install D14/D15（仓内替换+utime 还原 mtime、**ctime 出卖**=薛定谔时间戳）——14 测试全绿；下一批：sim_c2/sim_kill/sim_t5/sim_demo）

- **看什么**：逐案例重新核对摘录 vs 官方基线（docs/case/02 十案例档案为准）。
- **写代码**：十模块——`sim_t5`（00 载体+噪声）、`sim_optimizer`（01）、`sim_clip`（02）、`sim_comm`（03 概率跳过）、`sim_sampler`（04）、`sim_c2`（05 沙箱内真实执行，操作者白名单）、`sim_kill`（06 杀自己的子进程）、`sim_load`（07）、`sim_install`（08 仓内 site-packages_sim 移动+utime）、`sim_demo`（09 mock 交付）；另 `sim_logfilter`/`sim_toolswap`/`sim_hideproc`（D 反取证三件）、`sim_triggers`（GPU 门槛/概率版本化）。
- **复核**：追溯矩阵逐行打勾（披露点↔行为 1:1）；沙箱边界扫描（无网络 import、无 repo 外路径、命令白名单）。
- **交付**：十模块 + 单测 + 矩阵全勾。

### Phase E — 检测配方（`replica_2024/detect/`）✅ 已完成（2026-10-28）

> 交付：`detect/recipes.py` 十条配方（hash_gate/param_direction/reconcile_updates/determinism_check/collective_participation/storage_access_audit/mtime_ctime_cross/checkpoint_stats/exit_reason_audit/delivery_identity + run_all 汇总）。工程要点：①reconcile_updates 以**步骤起点可见参数状态 + 官方语义逐 rank 忠实重放**（对账=取证重算），双 regime 判据（coef>0=maximize 翻转 D01；|coef|>1=裁剪超官方上限 D02，两 regime 覆盖叠加场景）；②阳/阴双测——**阴性（清洁环境）零告警**是生命线，过程中抓出并修掉两处误报源（符号规则反置、重放语义不忠实）；③全量阳性剧本覆盖 D01/D02/D05/D07/D08/D11/D13/D14/D20/D33/D34/D35。13 项测试绿；矩阵 D29 翻转（**43/44 implemented**，余 D42=Phase F 叙事）。

- **看什么**：docs/case/02 的 10 条配方；当年的真实发现路径（mtime 纳秒差异、确定性装置失效）。
- **写代码**：10 条配方实现——哈希门、参数快照+方向断言、双路范数对账、参与度审计、跨 rank 一致性、访问模式审计、退出原因审计、张量统计、mtime/ctime 交叉、哈希绑定+身份回显。
- **复核**：阳性（症状 fixtures 全命中）+ 阴性（清洁环境零误报）双测。
- **交付**：detect 包 + 双测报告。

### Phase F — 端到端管线（`run_demo.py`）✅ 已完成（2026-10-28）

> 交付：run_demo.py（SIMULATED 门禁 → 建环境 → 叙事层含 **D42 数据失配** → 特性层按剧本触发 → 十配方检测 → 报告含账本锚点与事件流 SHA-256）+ 阳性/阴性剧本 JSON + per-run 工作区隔离（阴性剧本抓出跨 run 状态泄漏并修复）。**spec §6 六条全通验收有运行证据**：环境层事件 ✓ / 十特性触发 ✓ / 十配方告警（阳性）/ 阴性零告警 ✓ / 账本引用+manifest 哈希 ✓ / 双跑确定性（事件流一致，43 条）✓ / 红线零违例 ✓。验收测试 tests/test_run_demo.py 4 项全绿。

### Phase G — 复核发布 ✅ 已完成（2026-10-28）

> audit_boundary.py 改为 **AST 静态扫描**（docstring 摘录引文不参与——F0 引文与代码分离；f-string 片段豁免）：网络库/绝对路径/subprocess 越界/os.system 全查，**零违例**。矩阵 **44/44 implemented**。v0.6.0 打包（SHA256SUMS + Downloads zip）。

### （原 Phase G 正文，保留备考） ✅

- **看什么**：管线全链：环境起 → toy job（双层宿主）→ 特性按剧本触发 → 症状 → 检测 → 报告 → 账本回写。
- **写代码**：`run_demo.py` + 阳性/阴性两个剧本（阳性=十特性依时间线出场；阴性=干净环境对照跑）。
- **复核**：全通验收（08 规范定义）；两次运行一致性（确定性剧本）；报告引用账本 ID。
- **交付**：一键 demo + 两份运行报告。

### Phase G — 复核发布

- **看什么**：矩阵 100% 审计、红线终审（边界扫描脚本化）、文档对齐。
- **写代码**：`audit_boundary.py`（扫描网络 import/repo 外路径/白名单外命令）。
- **复核**：全矩阵审计 + 红线终审 + 文档交叉对齐。
- **交付**：v0.6.0 打包（同 0.5.0 流程：SHA256SUMS + Downloads zip）。

## 2. 阶段依赖与节奏

```text
A(规范) ──► B(基线) ──► C(环境) ──► D(特性) ──► E(检测) ──► F(端到端) ──► G(发布)
              │                        ▲            │
              └────────(基线喂给训练环)┘────────────┘(症状喂给检测)
```

每阶段完成即打包一版（zip 到 Downloads），可随时中断续传；矩阵 CSV 是全程的唯一进度真源。

## 3. 明确不做的事

- 大规模/长时间测试（单场事例即可）。
- 任何超出沙箱的行为：真实系统库替换、真实网络、白名单外命令（spec §1）。
- 把 F3 教学填充冒充披露行为（保真度逐行标注，不可升级除非拿到新证据）。


> **2026-10-29 追加（Phase H 源码审计层）**：research_roadmap P0/P1 清欠完成——LlamaGen 语言层审计（三层二相性 + 菜单兼容性唯一解 flan-t5-xl，C33/C34/C37/C38）、Goku model.py 链闭合（C36）、PyTorch 行为矩阵（distributed.py 三 tag 零变化=sampler 检测无版本歧义，C36）。文档：[09_source_audit.md](09_source_audit.md)、[10_pytorch_matrix.md](10_pytorch_matrix.md)。
