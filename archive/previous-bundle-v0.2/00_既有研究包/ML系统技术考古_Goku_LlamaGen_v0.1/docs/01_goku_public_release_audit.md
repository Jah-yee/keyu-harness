# 01｜Goku：论文、公开仓库与未公开工件

## 公开来源

- 论文：<https://arxiv.org/abs/2502.04896>
- CVPR 2025 Open Access：<https://openaccess.thecvf.com/content/CVPR2025/html/Chen_Goku_Flow_Based_Video_Generative_Foundation_Models_CVPR_2025_paper.html>
- 项目页：<https://saiyan-world.github.io/goku/>
- 公开 GitHub 仓库：<https://github.com/Saiyan-World/goku>

## 论文明确披露的内容

根据论文摘要与公开 PDF：
- Goku 是基于 rectified-flow Transformer 的联合图像/视频生成模型家族。
- 论文报告约 160M 图像—文本对和 36M 视频—文本对的数据规模。
- 论文描述 2B 与 8B 参数模型，以及 3D 联合图像—视频 VAE 和共享 latent 表示。
- 论文报告 GenEval 0.76、DPG-Bench 83.65、VBench 84.85 等评测结果。
- 论文描述为长序列训练采用的并行策略、激活检查点、ByteCheckpoint 与 MegaScale 相关容错机制。

这些信息能支持“公开论文如何描述模型与训练系统”，不能证明 2024 年每次内部训练使用完全相同的模型版本、配置或基础设施。

## 公开 GitHub 仓库的可见结构

当前公开仓库根目录列出：
- `configs/`
- `goku/`
- `tools/`
- `README.md`
- `requirements.txt`
- `.gitignore`

公开 `requirements.txt` 包含：
- `einops`
- `diffusers==0.32.2`
- `transformers==4.48.0`
- `huggingface_hub`
- `pandas`
- `cloudpickle`
- `omegaconf`
- `hydra-core`
- `ftfy`
- `beautifulsoup4`
- `av==12.0.0`

**版本注意：** 这是本次检查时公开仓库的当前依赖清单，不是 2024 年内部训练环境的依赖清单。

## 当前公开资料能否完整复现 Goku？

不能仅凭论文和仓库首页就认定可以端到端复现。当前仓库确实存在，且有配置、`goku/` 代码和 `tools/`；但首页 README 主要介绍模型和 benchmark，没有清晰给出完整训练数据、完整训练配方、历史训练作业日志或可核验的 2024 checkpoint provenance。仓库中具体代码覆盖范围仍应通过固定 commit 后逐文件审计。

## 对事件重建的意义

事件整理页称，2024 年 4 月起项目转向大规模视频生成，5—7 月出现频繁训练异常。公开论文提供系统级背景：大规模视频训练会涉及数据处理、模型、并行、checkpoint、容错和评估多个环节。它帮助列出应当调查的工件，但不能证明某个论文组件就是涉事故障的直接原因。

## 建议的源码审计清单

对固定的公开 commit 记录：
1. `git rev-parse HEAD` 和 `git status --porcelain`；
2. `configs/` 下每个配置文件的用途与引用关系；
3. `goku/` 下模型、pipeline、推理入口与外部依赖的边界；
4. `tools/` 下工件下载、预处理、评估或辅助脚本的输入输出；
5. requirements 与真实 import 使用情况的对应表；
6. 是否存在公开权重、训练脚本、数据 manifest 和 checkpoint 格式说明；
7. 公开 README 中哪些步骤能执行，哪些依赖未公开工件。

不要把“公开仓库存在”误解成“所有训练代码、数据和模型权重都已公开”。
