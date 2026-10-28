# 源码证据地图：从公开实现到可验证问题

> 2026-10-29：本文的路径级"应保存证据"已由 Phase B 兑现——pinned 快照在 `evidence/raw/`（llamagen@两 pin / goku@e29a217b / pytorch×4 tag），行级还原见 [case/02](case/02_code_reconstruction.md) 与 [case/09](case/09_source_audit.md)。本表保留为 v0.4 规划口径的存档。


> 公开代码路径是研究入口，不是"被修改文件"的既定名单；没有原始运行环境与工件链路时，历史修改位置保留为未知。
这份地图用于安排只读源码研究。它列出公开基线中的具体路径、可观察内容和下一步验证方式。**它不声称这些公开文件就是历史事件中被修改的文件，也不包含可执行的破坏性补丁。**

## 1. LlamaGen

公开仓库：<https://github.com/FoundationVision/LlamaGen>（来源 `S02`）

| 路径 | 当前可确认的用途 | 应保存的源码证据 | 与历史事件的关系 |
|---|---|---|---|
| `README.md` | 描述公开代码、模型工件、PyTorch 要求和采样命令 | 固定 commit、README、release 时间、相关行号 | 可帮助确定公开发布时点；不能代表 2024-03 内部 checkout |
| `language/README.md` | 当前文档指向 FLAN-T5-XL，并指定文档中的模型目录 | 固定 commit、文件内容、配置 URL | 是 XL/XXL 差异的对照材料，不是历史运行证据 |
| `autoregressive/sample/sample_t2i.py` | README 引用的文本条件采样入口 | 文件快照、参数定义、模型/缓存加载调用链 | 只读追踪公开输入与加载路径 |
| `autoregressive/sample/sample_c2i.py` | README 引用的类别条件采样入口 | 文件快照、checkpoint 参数和调用关系 | 用于理解公开采样流程 |
| `autoregressive/` | 自回归训练/采样相关代码区域 | 文件树、入口脚本、配置和测试 | 需要 commit 固定后再做细粒度分析 |
| `dataset/` | 数据集相关代码区域 | schema、预处理入口、数据清单和版本 | 不能凭目录名推断历史数据如何被处理 |
| `tokenizer/` | 图像 tokenizer 相关代码区域 | 模型配置、权重身份、编码/解码入口 | 与 T5 文本编码器属于不同工件链 |

官方 README 当前标注 PyTorch `>=2.1.0`，并列出 2024-06-11 与 2024-06-28 的公开发布节点。该时间信息对“公开代码何时可见”有帮助，但不证明内部早期版本不存在。

## 2. Goku

公开仓库：<https://github.com/Saiyan-World/goku>（来源 `S05`）

| 路径 | 当前可确认的用途 | 应保存的源码证据 | 限制 |
|---|---|---|---|
| `configs/` | 公开配置区域 | 文件树、配置 schema、被引用的配置文件 | 当前公开配置不等于历史内部配置 |
| `goku/` | 公开模型/系统代码区域 | 固定版本、模块依赖图、入口与调用关系 | 不能据此断言完整内部训练系统都已开源 |
| `tools/` | 公开辅助工具区域 | 文件清单、输入输出契约、依赖关系 | 不应仅凭目录名猜测工具职责 |
| `requirements.txt` | 公开依赖声明 | 固定 commit、文件内容和依赖版本 | 当前公开依赖不能回填到 2024 年环境 |

目前网页显示的 Goku 公开树属于 2025 年公开系统的研究入口。应先确定具体 commit，再对配置和调用关系做代码级说明。

## 3. T5 XL / XXL：配置身份检查

当前公开配置 revision：
- XL: `efd6532` — <https://huggingface.co/google/flan-t5-xl/blob/efd6532/config.json>
- XXL: `d2dd233` — <https://huggingface.co/google/flan-t5-xxl/blob/d2dd233/config.json>

| 字段 | XL | XXL | 用途 |
|---|---:|---:|---|
| `d_model` | 2048 | 4096 | 检查模型宽度 |
| `d_ff` | 5120 | 10240 | 检查前馈层宽度 |
| `num_heads` | 32 | 64 | 检查注意力头数 |
| `num_layers` | 24 | 24 | 检查 encoder 层数 |
| `num_decoder_layers` | 24 | 24 | 检查 decoder 层数 |

这些是特定公开配置 revision 的字段，不是权重 SHA。要识别历史任务真正加载的工件，还需要 tokenizer、权重 shard、缓存 manifest、加载路径和 job 记录。

## 4. PyTorch：正常行为基线

从明确的版本 tag 比较：
- `torch/utils/data/distributed.py`：DistributedSampler 的正常数据分配语义；
- `torch/distributed/`：分布式进程组和 collective API；
- `torch/serialization.py`：checkpoint 序列化/加载路径；
- `torch/nn/`：模型模块与参数更新相关的通用实现。

先记录三个 tag 的正常行为与测试，再讨论历史差异。没有实际运行环境的 package inventory、container digest 或 import path 时，不应把任意候选 tag 当作事故版本。

## 5. 研究记录格式

每个代码观察建议保存为一条记录：

```text
observation_id:
source_id:
repository:
commit_or_revision:
path:
line_range:
file_sha256:
observed_behavior:
normal_baseline:
claim_ids:
limits:
reviewer_status:
```

只有在确实保存了对应文件后，才填写 `file_sha256`。不要在本地文件缺失时复制一个看起来合理的哈希。

## 6. 安全边界

本仓库保留公开正常实现、版本比较、工件身份核验和合成异常检测。不会将事件材料中展示的破坏性片段组装成可运行攻击 harness，也不会把修改真实框架包、权重或训练任务的步骤作为教学 Demo。
