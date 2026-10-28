# 结论与行动 v1（2026-10-28）

## 一、当前可以"成立"的结论（按证据级别）

| # | 结论 | 级别 | 依据 |
|---|---|---|---|
| K1 | 研究项目训练受到恶意干扰，涉事实习生被辞退 | F2+F3 | 公司声明 + 多方报道收敛 |
| K2 | 3 月 LlamaGen T5 特征异常与 7 月 PyTorch 篡改被两源独立叙述 | F3 | S01 与 LP 双源（含同一 commit 截图） |
| K3 | 摘录与官方基线**技术相容**：4 个引用符号在 v2.1.0–2.4.0 逐字存在 | F1（本仓库实测） | 02_code_reconstruction §1/§2/§10 |
| K4 | 页面摘录**不完整**：wrapper 官方 0 命中 vs `_rank_not_in_group` 31 调用点 | F1（本仓库实测） | 02_code_reconstruction §5 |
| K5 | 被描述的持久化机制存在公开的机制级解释：就地修改 + 机器粘性（MegaScale 型 robust training） | F4-S01a + E1 论文机制 | issues #10 作者回复 + arXiv:2402.15627 |
| K6 | 27 个文件名清单两源吻合 | F1+F4 | S01 页面原文 + LP"27 个" |
| K7 | 共享存储（同组互写）是全链路中心信任边界 | H（被 F4 强烈支持） | 04_internal_environment §6 |
| K8 | "实习生A"前提受到实名反证 | F4（一方实名回应） | issues #9 |
| K9 | T5 型号差异（xxl vs xl）仍未解决 | U | U02 |

**不允许说的**：任何"某段代码被执行过""某次故障由某段代码造成"级别的因果结论；任何内部产品名/路径/个人身份的断言。

## 二、开放问题（按杠杆排序）

1. **U10 T5 载体实现**：改的是权重文件、加载 hook 还是序列化机制？——决定 B1 层是"数据投毒"还是"代码注入"，两者取证路径完全不同。→ 下一步：整理 PyTorch v2.2–2.4 时代 checkpoint/pickle 加载的公开风险面（含 v2.6.0 修复的反序列化问题作为"机制可能性"佐证），形成 `docs/case/07_checkpoint_carrier_surface.md`。
2. **U13 comm wrapper 完整 patch 范围**：31 个调用点如何被改写？→ 公开材料已穷尽；转 unknowns 登记，等待（或构造合成示意版本——只做"示意不完整"的教学展品，不做实现）。
3. **U02 T5 xl/xxl**：config 级对比已就绪，差一个"2024-03 时点公开版本"确认 → 与 LlamaGen commit 固定合并执行。
4. **E 层 barrier_vgpt 与 B1 的关系**：同一系统两代？两套？→ 保持 H，不做公开材料外的解读。
5. **版本断代收窄**：粗符号已证相容不可分辨 → 用更细表面（`# type: ignore` 注释版本、签名演化、foreach 路径、行号）做 `reference_analysis` 场景首个用例。

## 三、行动清单（下一阶段 = Harness 推进）

### 立即可做（无外部依赖）
- [x] **案例集完整化**：docs/case/02 已重写为十案例档案（每案含缺口清单与检测配方，合计 27 项缺口）
- [x] **全量参考文献页**：docs/references.md 已从账本渲染（S01–S33）
- [x] **脚注化**：主 README 已迁移为 GitHub 原生脚注（23 条定义，自动回链）；英文版 README_EN 同步上线
- [ ] **机制主张入账**：C17–C28 批量写入 claim_ledger（本次已随文档落库，见 references/）
- [ ] **S01 仓库 pin**：clone keyu-tian-sabotage.github.io @ `e4292f48b3ad` + tree manifest → S01 升级 HASHED
- [ ] **capture.py**：把本轮手工捕获流程固化为 `keyu-harness capture <url> --ref <sha>`（写 manifest、更新 artifact_registry 状态）
- [ ] **检测配方 1&2 实现**（展品 A/D 最易）：`scenario kind=reference_analysis` + 合成 fixture 断言
- [ ] **issues 全量抓取**：12 条 issue 正文+评论全部入 evidence/raw（本轮已抓 2 项）

### 需要一轮外部检索/抓取
- [ ] 品玩已捕获；虎嗅被反爬 → 换渠道（存档站/转载）补 S31
- [ ] elsewhere 10-19 调查说明全文（当事人版本降权的关键佐证）
- [ ] 12 月学术伦理投诉信原始 repo 定位
- [ ] VAR 官方仓库 issues 的伦理讨论抽样（仅作来源登记）
- [ ] anti-keyu-tian 仓库通读，检测配方对照

### 需要固定公开基线（P0 老三项）
- [ ] LlamaGen 2024-03~08 commit 考古 + README/language README pin（U01）
- [ ] PyTorch 2.2/2.3/2.4 三 tag × 5 文件 diff 矩阵（U05/K3 收窄）
- [ ] flan-t5-xl/xxl config+tokenizer 捕获与对比报告（U02/K9）

### 中期（工程化）
- [ ] artifact_registry 增加 `deployment_layer` 维度字段（A–E）
- [ ] Mechanism 实体 schema（摘录/基线/语义/缺口四件套）
- [ ] `docs/case/07_checkpoint_carrier_surface.md`（见开放问题 1）
- [ ] CI：unittest + validate-ledger + 新增 manifest 哈希自检

## 四、本阶段方法论沉淀（可复用）

1. **对质驱动澄清**：第三方质疑（issues #10）逼出了三条最关键的机制澄清——质疑不是敌人，是免费的取证压力测试。
2. **症状层复刻**：装置只复刻"被观测到的后果"，不复刻实现——既保教学价值又守住红线（fixtures/virtual_environment_v2 的设计原则）。
3. **机制四件套**：每条机制主张 = 摘录（E4）+ 官方基线（E1 实测）+ 语义效果（H）+ 缺口清单——这个格式已被 02_code_reconstruction 验证可行，值得升格为 schema。
4. **锚点标注**：虚构装置的每个"真实锚点"用 `[REPORTED-BASIS: …]` 内联标注，让读者随时能分清考古与填充。
