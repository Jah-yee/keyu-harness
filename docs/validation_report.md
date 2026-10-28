# 验证报告（2026-10-29 快照）

**本页是仓库体检的时点快照**——持续验证由 CI 与 tests/ 承担；每次发布按 [release_checklist](release_checklist.md) 重生成。

| 检查项 | 结果 |
|---|---|
| 单元测试 | ? |
| 来源账本（34 条） | PASS |
| 主张账本（38 条） | PASS |
| 工件账本（17 条） | PASS |
| 追溯矩阵 | 44/44 verified |
| 阳性剧本（十特性+打窝+部署链） | ALL_PASS |
| 阴性剧本（清洁对照） | ALL_PASS + 零告警 |
| 沙箱红线 | audit_boundary: 0 violations over replica_2024/ |

## 解读

- PASS 验证的是工具链与合成具身的健康度，不构成对历史事件事实的证明（见[证据模型](evidence_model.md)）。
- 历史版本（v0.4.0 时点）的验证报告见 git 历史——本页只保留当前快照。
