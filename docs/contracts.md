# 契约 Contracts

**本仓库对外承诺的可检验不变量。** 每条契约 = 一句承诺 + 执行机制 + 验证位置。违反任何一条都是 bug——不是风格问题。

| # | 契约 | 执行机制 | 验证位置 |
|---|---|---|---|
| C-A | **沙箱封闭**：`fixtures/replica_2024/` 内无网络库 import、无绝对路径字面量、subprocess 仅限声明模块、无 os.system | `audit_boundary.py`（AST 扫描，docstring 摘录引文豁免） | CI 第 5 步；tests/test_run_demo.py |
| C-B | **账本自洽**：四张 CSV（来源/主张/工件/追溯矩阵）schema 合法、ID 交叉引用可解析、状态词汇合法 | `keyu-harness validate-ledger` ×3 | CI 第 3 步 |
| C-C | **管线全通**：阳性剧本十特性全部触发、十条配方全部告警；阴性剧本零告警 | `run_demo.py` 内建验收 | CI 第 4 步；tests/test_run_demo.py |
| C-D | **确定性**：同一确定性剧本两次运行的事件流逐条一致（逻辑时钟；真实时间值不入事件流） | 双跑比对 | tests/test_run_demo.py |
| C-E | **保真度诚实**：每个披露点标 F0–F3，F3 永不冒充 F0；升级须有新证据并记录 | 追溯矩阵评审（人工）+ 摘录逐字断言（F0 项在单测中验证源码含逐字行） | tests/test_harness_features.py |
| C-F | **零运行时依赖**：L0 宿主与 CLI 仅用标准库；torch 走 `.[sim]` extras | pyproject extras 声明 + import 扫描 | tests（无 torch 环境即验证） |
| C-G | **引文保真**：引用报道/页面原文时逐字不改，转述与直接引语分离 | 评审（对照 evidence/raw/ 捕获件） | docs/case/01、02 |
| C-H | **发布可自检**：每个发布 zip 内含 SHA256SUMS.txt，包内逐文件哈希可对账 | 打包流程（git archive + Python zipfile 对账） | 每次发布的自检步骤 |

## 与其他文档的关系

- 红线的"为什么"：[principles.md](principles.md)
- 复刻侧的完整规范：[08_replication_spec.md](case/08_replication_spec.md)（本文档的 C-A/C-C 由其 §1/§6 具体化）
- 违例的实例教学：CHANGELOG 0.6.1（代码审查轮次清查的 10 处问题）
