# 贡献指南 Contributing

> 先读[主 README](README.md) 的「规矩」四条——那是本仓库的宪法。本页是宪法的实施细则。
> 一句话版本：**梗要挂出处，代码要跑测试，报告要有出处，指人不指名。**

## 我们收什么

| 类型 | 去哪 | 要求 |
|---|---|---|
| 新披露点 / 新来源 | Issue（[证据与纠错模板](.github/ISSUE_TEMPLATE/evidence-or-correction.md)） | 链接 + 日期 + 发布者；一句话主张 |
| 主张纠错 / 叙述补充 | Issue → 对质矩阵 | 说明与既有叙述的关系（支持/矛盾/独立） |
| 代码（检测配方 / 宿主 / 复刻模块） | PR | 挂钩子面、带单测、过红线扫描 |
| 文档与翻译 | PR | 保持「英文管它是什么、中文管它为什么对得上」的双语分工 |
| 弹幕 | PR（评论行） | 见下方弹幕守则 |

## 红线（PR 会被直接关闭的事）

1. **可运行的攻击或规避代码**。复刻模块只复刻"被观测到的症状"；沙箱边界（无网络、无 repo 外写入、命令白名单）由 `audit_boundary.py` 静态扫描，CI 会拦。
2. **指认任何具体个人**：目录名、模糊报道、聊天记录截图都不构成指认依据。实名背书信息只链接、不复制。
3. **F3 冒充 F0**：教学填充必须标 `SIMULATED`/`FICTIONAL`，永不混入 `evidence/raw/`。
4. **无出处的断言**：每条主张挂来源编号；"大家都这么说"不是来源。

## 弹幕守则（本仓库唯一的幽默规范）

弹幕（`💬`）是本仓库的叙事层。合格弹幕的三条标准：

1. **它必须能被溯源**——读者点开对应主张的出处后应该会心一笑，而不是困惑。例：「薛定谔的时间戳：观测之前，改没改过处于叠加态」对应的是 S01 卡片 8 的 `os.utime` 与 LatePost 的纳秒 mtime 细节。
2. **它只翻译事实，不发明事实**——数字、路径、人名都不许编。
3. **它不指向人**——讽刺对象是被报道的工具与荒诞的处境，永远是。

不合格示例（并说明为什么）：~~"牢 X 干得漂亮"~~（指人）；~~"大厂员工都是草台班子"~~（扩大打击面）；~~"这肯定是 AI 写的"~~（无出处）。

## 账本纪律（改 CSV 前必读）

- `references/` 下四张表是**进度与主张的唯一真源**：来源（source_registry）、主张（claim_ledger）、工件（artifact_registry）、追溯矩阵（traceability_matrix）。
- 改动后必须跑：
  ```bash
  PYTHONPATH=src python -m keyu_harness validate-ledger sources references/source_registry.csv
  PYTHONPATH=src python -m keyu_harness validate-ledger claims references/claim_ledger.csv
  PYTHONPATH=src python -m keyu_harness validate-ledger artifacts references/artifact_registry.csv
  python -m unittest discover -s tests
  ```
- 来源角色、取得状态、主张状态是三个不同的字段，回答三个不同的问题（详见[证据模型](docs/evidence_model.md)）。转载稿不算独立交叉验证。
- 没取得的材料：`sha256` 与 `local_path` 留空。不能因为"浏览器打开过"就填哈希。

## PR 清单

- [ ] `python -m unittest discover -s tests` 全绿
- [ ] 三账本 `validate-ledger` 通过
- [ ] 若动过 `replica_2024/`：`audit_boundary.py` 零违例 + 两剧本 ALL_PASS
- [ ] 新主张挂了来源编号，写明局限与替代解释
- [ ] 新弹幕通过上面三条标准
- [ ] 没有新增第三方运行时依赖（双层宿主的 torch 走 `.[sim]` extras）

## 语言分工

英文管"它是什么"（API、事件字段、CLI、机器可读输出）；中文管"它为什么与披露对得上"（注释、弹幕、研究文档）。中文来源保留原题。完整规范见[复刻规范 §8](docs/case/08_replication_spec.md)。

## 致谢与引用

引用方式见 [CITATION.cff](CITATION.cff)。本仓库大量引用记者与受害方整理者的公开工作——他们是这份档案能存在的第一因；引用时请保留原题与链接。
