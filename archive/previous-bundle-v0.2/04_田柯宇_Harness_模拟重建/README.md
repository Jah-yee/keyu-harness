# 田柯宇 Harness 模拟重建（虚构教学环境）

> 本目录不是当事人真实仓库，也不是原始攻击 harness。所有账户、目录、job ID、模型注册表和日志均为虚构教学样本。

## 目标

展示一个可审计的 ML 训练工作流模拟器如何：
1. 接收一个受限 JSON 场景请求；
2. 验证场景 schema；
3. 读取合成模型登记、日志和来源元数据；
4. 生成事件序列与风险提示；
5. 输出 `report.md`、`report.json`、`events.jsonl` 与 SHA-256 manifest。

模拟器没有任意 shell/代码执行功能，也不修改真实源码、PyTorch 安装、权重或正在运行的训练任务。

## 运行

```bash
python -m thal.cli run scenarios/t5_metadata_mismatch.json --out outputs/t5-demo
python -m thal.cli run scenarios/distributed_trace_anomaly.json --out outputs/trace-demo
python -m thal.cli hash-manifest virtual_workspace --out outputs/workspace-manifest.json
python -m unittest discover -s tests -v
```

## 组件地图

- `thal/cli.py`：命令行入口和参数校验。
- `thal/scenario.py`：读取场景 JSON、限制字段、生成事件。
- `thal/evidence.py`：哈希清单和报告生成。
- `scenarios/`：完全合成的输入案例。
- `virtual_workspace/`：虚构的用户、组织、公开项目基线、模型登记和训练作业目录。
- `tests/`：检查 schema、检测逻辑与证据输出。

## 虚构目录约定

`engineer-017`、`reviewer-002`、`job-sim-2024-03-017` 都是随机教学标签，不指向真实人员或组织架构。不得将此目录截图或日志引用为事件原始证据。
