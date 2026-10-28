# 02｜LlamaGen：公开训练链与模型工件

## 公开来源

- GitHub：<https://github.com/FoundationVision/LlamaGen>
- 论文：<https://arxiv.org/abs/2406.06525>
- 作者项目页：<https://peizesun.github.io/llamagen/>
- Hugging Face 模型集合：<https://huggingface.co/FoundationVision/LlamaGen>
- 当前语言模型说明：<https://github.com/FoundationVision/LlamaGen/blob/main/language/README.md>
- Getting Started：<https://github.com/FoundationVision/LlamaGen/blob/main/GETTING_STARTED.md>

## 公开仓库的主要目录

| 目录 | 公开用途/研究切入点 | 本次需要记录的工件 |
|---|---|---|
| `autoregressive/` | 自回归模型训练、采样与 serving | 入口脚本、配置、模型定义、checkpoint 读写路径 |
| `dataset/` | 数据适配 | 数据版本、预处理和缓存约定 |
| `evaluations/` | 评估 | 评估脚本版本、数据集版本、指标输入输出 |
| `language/` | 文本条件生成所需语言模型依赖 | T5 型号、tokenizer、Transformers 版本、缓存特征生成说明 |
| `scripts/` | 训练与数据处理 shell 脚本 | 启动参数、DDP/FSDP 参数、数据路径、输出路径 |
| `tokenizer/` | 图像 tokenizer/VQ 组件 | tokenizer checkpoint、离散 code 的生成与消费 |
| `tools/`、`utils/` | 辅助工具和通用逻辑 | 文件 I/O、日志、模型保存、采样辅助逻辑 |

## 公开模型和结果

当前 README 表示仓库公开训练/采样 PyTorch 代码与预训练权重，并说明：
- 图像 tokenizer 包含下采样比例 16 和 8 的版本；
- 类条件模型规模约 111M 到 3.1B 参数；
- 文本条件模型约 775M 参数；
- 文本条件阶段一：LlamaGen-XL，256 分辨率/16×16 tokens，使用 LAION-COCO（50M）；
- 文本条件阶段二：LlamaGen-XL，512 分辨率/32×32 tokens，使用内部数据（10M）；
- 文本条件 tokenizer `vq_ds16_t2i` 标记为 72M 参数，README 数据栏写 LAION-COCO 50M + internal data 10M；
- README 公开了部分模型权重下载链接和采样入口。

这些公开 checkpoint 是论文/仓库发布的研究工件，不自动等于 2024 年事故时内部使用的文件，更不自动等于被报告修改的 T5 文件或文本特征缓存。

## 训练数据流（公开实现抽象）

```text
图片/文本数据
  ├─ 图像 tokenizer / VQ 组件 → 离散图像 tokens
  └─ T5 文本编码器 + tokenizer → 文本条件特征
                                  ↓
自回归 Transformer 学习图像 token 序列
                                  ↓
checkpoint / 采样 / 评估
```

要区分三种不同工件：
1. **T5 权重**：文本编码器的模型参数；
2. **文本特征缓存**：T5 对特定文本、tokenizer、截断规则和预处理版本生成的张量；
3. **LlamaGen 主模型 checkpoint**：学习视觉 token 序列的自回归模型参数。

这三者不是同一个文件，也不能用其中一个的哈希替代另两个的来源证明。

## 对事件材料的意义

事件整理页称 2024 年 3 月的异常涉及 `flan-t5-xxl` 权重/文本特征。当前公开 `language/README.md` 写的是 `flan-t5-xl`。这个差异必须作为一个独立待核事项，而不能仅凭当前 README 就否定或确认事件材料。

下一步需要历史仓库 commit、实际模型配置、tokenizer 文件、权重哈希和缓存 manifest。当前 `main` 只能作为当前公开实现基线。
