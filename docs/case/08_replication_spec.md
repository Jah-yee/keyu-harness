# 复刻规范 Replication Spec（Phase A 交付）

**性质：工程规范。本文件是 v0.6 复刻计划的约束层——先有规范，后有代码。**

## 1. 沙箱红线（唯一保留的一条红线）

**完整功能复刻，环境锁死。** 模拟世界的"系统"就是仓库目录，因此：

1. **无网络**：`replica_2024/` 内任何模块不得 import 网络库、发起任何网络调用。边界扫描脚本（`audit_boundary.py`）静态检查。
2. **无 repo 外写入**：所有文件操作（含"已安装库替换"、共享盘轮询、日志）限定于 `fixtures/replica_2024/` 内部。模拟环境的 `site-packages_sim` 就是它的"系统"——在其中移动文件即"sudo 替换系统库"的全部语义，真实系统库不存在也不需要触碰。
3. **进程边界**：sim 杀伤的进程只能是本 demo 自己派生的子进程。
4. **操作者白名单**：特性 05 的"命令执行"以脚本化操作者写入命令文件；操作者命令限定白名单（echo/cat/ls 等只读演示命令），白名单外命令被记录并拒绝执行——这本身就是对"沙箱纪律"的示范。
5. **SIMULATED 事件流**：每个模块的每次行为都 emit 结构化事件（`sim_event.jsonl`），事件含 module/feature/disclosure_id/行为/时间戳。

红线与"完整功能复刻"不冲突：**模拟世界就是整个世界**——在该世界内，十特性全部按真实语义运行。

## 2. 保真度分级 F0–F3

| 级别 | 定义 | 例 |
|---|---|---|
| **F0 摘录逐字复现** | 公开摘录的代码语义逐字落进模拟环境 | maximize 行、clip×2 行、sampler 种子行、nan_to_num 行、os.utime 行、modify_t5 |
| **F1 摘录推导** | 摘录存在但需适配（调用点/宿主差异），推导部分标注 H | comm wrapper（31 调用点的模拟改写）、确定性探测器、`__pycache__` 生成 |
| **F2 功能对齐** | 无公开代码，按披露的功能描述实现等效行为 | T5 载体读目录执行、wait.py 命令执行、kill 定点终止、安装器移动+还原、日志删行、工具替换、进程隐藏、VAR Demo 顶替、机器粘性、存储恢复 |
| **F3 教学填充** | 披露仅及背景或无细节，按合理设定填充 | 领导目录名下的具体文件、资源池争用数值、排障群规模、剔机剧情参数 |

规则：F3 永不冒充 F2 及以上；矩阵逐行标注；升级保真度必须有新证据并记录。

## 3. 1:1 追溯矩阵 schema（`references/traceability_matrix.csv`）

| 列 | 含义 |
|---|---|
| disclosure_id | 披露点 ID（D01…） |
| category | 类别（特性/散布/反取证/部署链/环境/取证史） |
| disclosure | 披露点描述（原文口径） |
| source | 来源（S01/S10/S28…） |
| fidelity | F0–F3 |
| module | 实现模块（replica_2024 内路径） |
| trigger | 触发方式（何时/何条件生效） |
| expected_symptom | 预期症状（可观测后果） |
| detection | 对应检测配方 |
| evidence_grade | 证据级别（REPORTED/CLARIFIED/FILLER） |
| status | planned / implemented / verified |

**1:1 的验收 = 矩阵中每行 status=verified，且每行都能在 demo 运行中指认。**

## 4. 目录与命名规范

```text
fixtures/replica_2024/
  env/                 # 环境复原（feishu_sim/scheduler/storage/stickiness/ejector/authlog/pool）
  site-packages_sim/   # 模拟"已安装 torch"（含被替换前/后两套）
  train/               # 双层宿主：mini_loop.py（stdlib）/ torch_loop.py（extras）
  harness/             # 十特性模块 + sim_triggers + 反取证三件（sim_ 前缀）
  operator/            # 脚本化操作者（白名单命令剧本）
  detect/              # 10 条检测配方
  scenarios/           # 阳性/阴性剧本（JSON：何时触发何特性）
  run_demo.py          # 端到端管线
  sim_event.jsonl      # SIMULATED 事件流（运行产物，不入 git 语义层）
  audit_boundary.py    # 沙箱边界扫描
```

命名：模块 `sim_` 前缀；剧本 JSON 含 `notice: "FICTIONAL RECONSTRUCTION"`；所有输出报告 data_class=SIMULATED。

## 5. 双层宿主规范

- **L0（默认，纯标准库）**：线性模型 + 合成数据的梯度下降环；rank 为进程内对象；梯度/损失/采样语义完整，数值保真度低。人人可跑。
- **L1（extras `.[sim]`，torch）**：真实张量、真实 DistributedSampler/clip_grad/optimize 语义被替换前的原版行为可直接调用对照；单进程顺序模拟多 rank。
- 两层共用同一 harness 接口：特性模块对宿主只依赖 `Trainer` 抽象（get_params/step/load_checkpoint/collective 等），L0/L1 各提供实现。

## 6. "管线全通"验收定义

一次 `run_demo.py --scenario scenarios/positive.json` 达到：

1. 环境层事件（会议、存储、调度）≥ 各 1 条且与报道对照表吻合；
2. 十特性各触发 ≥1 次，事件流含对应 disclosure_id；
3. 十条检测配方各产出 ≥1 条告警（阳性剧本）/ 0 条（阴性剧本）；
4. 报告引用账本 ID（claim/disclosure），输出 manifest 哈希；
5. 两次运行的确定性剧本事件序列一致（时间戳除外）；
6. `audit_boundary.py` 零违例。

## 7. 与既有体系的关系

- 追溯矩阵是 `unknowns.csv` 的下游：缺口清单项若在复刻中获得"机制理解"，不改写历史未知项状态——复刻是 SIMULATED 层，永不回写历史证据层。
- 主张账本新增 C 系列时引用矩阵 disclosure_id 作为"实现参照"，但复刻行为本身永远不构成历史主张的证据。
- 本规范冲突时优先级：沙箱红线 > 保真度诚实 > 1:1 覆盖 > 演示效果。


## 8. 语言层规范（replica 代码的语言权衡）

| 层 | 语言 | 例 |
|---|---|---|
| 标识符 / 事件字段 / CLI | 英文 | `sim_optimizer.apply_maximize`、`disclosure_id` |
| docstring | 首行英文 + 正文中文 | `"""Feature 01 — Maximize the Loss.` + 中文详注（出处锚点） |
| 注释 | 中文 | `# F0 摘录行（语义逐字）`——注释承载出处锚点（A/B/C 级、D 编号、卡片引用），读者是中文研究者 |
| 弹幕 / 叙事 note | 中文 | `💬 优化器反着跑`、`note="沙箱内真实执行（白名单内）"` |
| 机器可读输出 | 英文 | 事件流字段值、manifest、报告 data_class |

理由：本仓库的语言约定（中文=研究叙事、英文=机器层）在 replica 里表现为——**英文负责"它是什么"，中文负责"它为什么与披露对得上"**。Danmaku 是叙事层，中文是它的母语。
