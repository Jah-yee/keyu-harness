# 发布清单 Release Checklist（v0.7 实际流程）

以 v0.6.0/v0.7.0 的实际打包步骤为准：

1. **定版**：CHANGELOG 条目（Unreleased → 版本号 + 日期 + 主题）、pyproject.toml `version`、CITATION.cff `version` 三处同步。
2. **终回归**：`PYTHONPATH=src python -m unittest discover -s tests` 全绿（torch 缺席时 3 项 skip 属正常）；三账本 `validate-ledger` 全 valid。
3. **红线终审**：`python fixtures/replica_2024/audit_boundary.py` → 零违例。
4. **端到端**：阳性/阴性两剧本 ALL_PASS（run_demo 内建验收）。
5. **清理**：删除 `__pycache__/`、`.DS_Store`、`fixtures/replica_2024/outputs/`（运行产物不入包，runbook 可复现）。
6. **哈希清单**：`find . -type f ! -name "SHA256SUMS.txt" ! -name ".DS_Store" | sort | xargs shasum -a 256 > SHA256SUMS.txt`。
7. **打包**：git 提交后 `git archive --format=zip --prefix="Keyu_Harness/" -o ~/Downloads/Keyu_Harness_<版本>_<日期>.zip HEAD`。
8. **包内自检**：用 Python zipfile（勿用 macOS unzip——对 git archive 的 UTF-8 路径有兼容问题）逐文件对账 SHA256SUMS，全部 OK 才交付。
9. **登记**：CHANGELOG 补打包记录；若为公开版，GitHub 网页下载/克隆不受上述 unzip 兼容问题影响。
