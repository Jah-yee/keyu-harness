# 架构说明

## 核心设计

Keyu Harness 是一个来源与工件驱动的研究工作台，研究**对象**是被报道的田柯宇攻击 harness。它不是以“事件故事”为数据模型，而是围绕三种实体组织：

- **Source**：一份可定位的材料；
- **Claim**：一条需要核验的陈述；
- **Artifact**：一个具体的软件版本、配置、权重、缓存、环境或日志对象。

三者通过稳定 ID 关联。CLI 负责校验和报告，不能替代来源本身。正在成形的第四种实体是 **Mechanism（机制）**：每条机制主张的四件套——摘录（E4）、官方基线（E1 实测）、语义效果（H）、缺口清单，格式已在 `docs/case/02_code_reconstruction.md` 验证。

## 三层工作方式

```text
考古（Archaeology）   来源捕获 → 版本固定 → 主张入账 → 交叉验证
装置（Installation）  症状层展品 → [REPORTED-BASIS] 锚点 → 可走查 → 反向检验考古完整性
检测（Detection）     展品 ↔ 检测配方一一对应 → 在合成 fixture 上实现
```

装置是架构中的一等公民：不是文档的插图，而是考古结果的可执行呈现，同时充当检测配方的靶场。铁律：装置只复刻"被观测到的症状"，不复刻实现。

对外文体说明：主 README 采用"案件卷宗/训练优化"的产品建档体例（核心叙事：优化 loss 之外的一切——九维提升；含讽刺性语体与文献包装），属于呈现层；本章的"考古/装置/检测"分层与机制四件套是内部工作词汇。两套语言的映射：README 的"特性"= 本档的 Mechanism（C17–C29），"现场复原"= fixtures/virtual_environment_v2，"检查方法"= 检测配方。

## 研究对象的关系

```text
Source ───── supports / limits ─────> Claim
  |                                     ^
  | identifies                           | tested by
  v                                     |
Artifact ───── produced / consumed ─> Run
  |                                     |
  └──── version / hash / manifest ──────┘
                |
                v
     Installation exhibit（症状层展品，SIMULATED）
```

这张图中的关系只有在有材料支持时才填写。没有来源的内部目录、权重或日志不应以“合理猜测”方式写进历史实体表。展品可以引用主张（作为锚点），但展品本身永远不进入历史实体表。

## 目录职责

| 路径 | 职责 |
|---|---|
| `src/keyu_harness/` | CLI、合成场景、清单生成和表格校验 |
| `scenarios/` | 英文合成案例 |
| `fixtures/simulated_workspace/` | 第一代虚构教学工作区与日志 |
| `fixtures/virtual_environment_v2/` | 实验装置 v2：可走查的环境切片（组织、作业生命线、症状展品） |
| `references/source_registry.csv` | 来源类型、URL、版本与取得状态 |
| `references/claim_ledger.csv` | 主张、支持关系、状态和缺失材料 |
| `references/artifact_registry.csv` | 软件/模型工件、revision、哈希与生产/消费关系 |
| `references/unknowns.csv` | 仍未取得的材料与下一步动作 |
| `references/bibliography.bib` | 论文与软件的书目元数据 |
| `evidence/raw/` | 依法取得/公开来源的原始捕获，只读保存（现有 6 项带哈希） |
| `evidence/manifests/` | 文件清单、哈希与采集元数据 |
| `evidence/derived/` | diff、图表、解析输出和报告 |
| `evidence/simulated/` | 合成材料，与真实材料隔离 |
| `docs/case/` | 本案研究线：事实提取、代码还原、部署链、内部环境、对质矩阵、结论与行动、复刻计划（07）与复刻规范（08） |
| `fixtures/replica_2024/` | **可运行复刻**：双层宿主（L0 stdlib / L1 torch extras）、harness 十一模块（十特性 + 反取证三件 + 触发器）、detect 十配方、env 七模块、operator/scenarios、run_demo.py 端到端、audit_boundary 沙箱终审 |
| `detect/`（replica 内） | 检测配方：hash_gate / param_direction / reconcile_updates / determinism_check / collective_participation / storage_access_audit / mtime_ctime_cross / checkpoint_stats / exit_reason_audit / delivery_identity |
| `docs/principles.md` | 价值观层：为什么这么做 |
| `docs/contracts.md` | 契约层：八条可检验不变量与执行机制 |
| `docs/changes.md` | 设计变更日志：决策转向与被否决方案 |
| `docs/scaling.md` | 方法扩展性：把本案模板带到下一场事故 |
| `docs/` | 中文研究说明、源码地图和方法规范 |
| `archive/` | 历史版本与迁移记录 |

## 数据流

```text
公开来源 / 合法取得的原始材料 / 合成场景
                  |
                  v
      Source registry + artifact manifest
                  |
                  v
    版本固定 -> 文件哈希 -> schema 校验
                  |
        +---------+---------+
        v                   v
  公开源码对照 /          装置展品建造
  工件身份检查 /          （症状层 + REPORTED-BASIS 锚点）
  日志审计                     |
        |                      v
        |               检测配方实现
        |                      |
        +---------+-----------+
                  v
     Claim ledger + reproducible report
                  |
                  v
      可复核结论 + 明确的未知项
```

## 分层总图（v0.7）

```text
价值观  principles.md ──约束──► 契约  contracts.md ──强制──► CI
研究    research_methodology + evidence_model ──产出──► 账本四表
档案    README（卷宗）+ docs/case/ ──呈现──► 现场 fixtures/virtual_environment_v2
复刻    fixtures/replica_2024（env + train + harness + detect）──► run_demo 端到端
发布    release_checklist ──► SHA256SUMS + zip（包内自检）
```

## 工程改进方向

当前工具已经可以运行合成场景、计算文件哈希、生成报告并校验 CSV（来源 33 / 主张 29 / 未知项 13，三表交叉校验通过）。下一步最有价值的工程改进是：

1. **capture 命令**：把手工捕获流程固化为 `keyu-harness capture <url> --ref <sha>`（下载、哈希、写 manifest、联动更新 artifact_registry 状态）。
2. **reference_analysis 场景类型**：data_class=E1 的真实公开材料分析场景（首个用例：PyTorch API 表面断代），与 SIMULATED 门禁并存。
3. **报告 ↔ 账本联动**：报告引用来源/工件/主张 ID，并新增 validate-report 校验引用可解析。
4. **工件谱系**：artifact_registry 增加 `deployment_layer`（A 散布/B 触发/C 持久化/D 反取证/E 通道）维度与 producer/consumer 图渲染。
5. **Mechanism schema**：机制四件套升格为机器可读格式。

所有检测结果都应被表述为“发现了某种差异/异常”，除非完整因果链另有证据。

> 2026-10-29 更新：本文件已覆盖 v0.7 形态（复刻层/检测层/新文档链接）。历史版本见 git。
