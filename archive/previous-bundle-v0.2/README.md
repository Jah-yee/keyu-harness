# THAL — Tian Harness Archaeology Lab
## 田柯宇 Harness 技术考古与模拟重建实验室

**版本：v0.2｜研究与教学用途｜日期：2026-10-26**

THAL 是一个 evidence-first（证据优先）的研究仓库，用公开论文、公开源码、公开模型卡和可复核的合成实验，研究 Goku、LlamaGen、T5 与 PyTorch 训练工件之间的关系。

> **重要声明：** 本项目不是涉事人员真实的 harness，也不声称获得任何内部 GitLab、飞书、训练日志、镜像或模型文件。`04_田柯宇_Harness_模拟重建/virtual_workspace/` 中所有组织目录、账户、job、路径和日志都是明确标记的虚构教学样本。项目不包含真实攻击代码，不修改真实仓库、PyTorch 安装或模型权重。

## 本阶段的目标

1. 保留上一阶段 Goku/LlamaGen/T5/PyTorch 的研究文档。
2. 建立可复核的 2024 历史基线：区分当时可用的公开版本、后来才公开的研究工件，以及未知的内部版本。
3. 建立虚构、只读的模拟工作区，演示一个 harness 的组成：请求入口、场景解析、工件登记、事件记录、证据清单和报告生成。
4. 用安全的合成场景复现“元数据不一致”“rank 指标异常”“来源链缺失”等可观察问题。
5. 保留证据等级、来源 URL、哈希、时间线和缺失证据清单，让研究者能继续补强真实证据。

## 术语选择

比“攻击复刻”更准确的名称是 **机器学习系统技术考古（ML Systems Archaeology）与模拟重建（Simulation Reconstruction）**。它结合数字取证、软件供应链分析、可复现实验和调查来源批判。

## 快速开始

仅依赖 Python 标准库（Python 3.10+）：

```bash
cd 04_田柯宇_Harness_模拟重建
python -m thal.cli run scenarios/t5_metadata_mismatch.json --out outputs/t5-demo
python -m thal.cli run scenarios/distributed_trace_anomaly.json --out outputs/trace-demo
python -m thal.cli hash-manifest virtual_workspace --out outputs/workspace-manifest.json
python -m unittest discover -s tests -v
```

所有命令只读取仓库里的合成 JSON/CSV/Markdown，并把结果写入指定的 `outputs/`；不会连接内部系统，不会下载或修改第三方仓库，不会触碰真实训练作业。

## 目录导航

- `00_既有研究包/`：上一阶段研究成果归档（若本地副本可用则完整保留）。
- `01_项目定义与方法/`：范围、架构、证据等级、模拟原则。
- `02_历史基线_2024/`：公开时间线、版本基线、历史版本取证规则。
- `03_来源与证据账本/`：来源登记、主张矩阵、证据缺口。
- `04_田柯宇_Harness_模拟重建/`：独立的教学 harness；`virtual_workspace/` 内所有目录均为虚构。
- `05_复核清单与下一阶段/`：交付验收、优先研究任务与未决问题。

## 证据纪律

- E1：公开原始工件（官方源码、论文、模型卡、release）。
- E2：组织/作者公开声明。
- E3：有交叉核实的独立报道或多方采访。
- E4：单方叙述、事件整理页、未经独立保全的代码摘录。
- E5：系统层推断。
- U：缺少足够材料、暂时未知。

网页上公开展示的代码摘录，不能自动等同于已独立保全的原始 Git 对象、容器镜像或内部日志。

## 当前最重要的已知限制

- LlamaGen 当前公开仓库 README 记录了 2024-06 的代码/模型发布；它不自动代表 2024 年 3 月的内部 checkout。
- Goku 论文发布于 2025-02；当前公开 Goku 仓库不能被当作 2024 年内部源码的直接替身。
- PyTorch 2.2.0、2.3.0、2.4.0 的发布时间可作为版本时间窗参考，但不能推断涉事机器实际安装了哪个版本。
- T5 XL/XXL 差异尚需历史 commit、真实配置、文件哈希与缓存来源链解决。
