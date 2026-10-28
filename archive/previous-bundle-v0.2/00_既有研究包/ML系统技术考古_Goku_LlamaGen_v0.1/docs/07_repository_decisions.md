# 07｜仓库决策记录

## 决策 1：以 Goku 和 LlamaGen 为主

VAR/PixArt 不进入当前主线。它们只在早期工作区中作为背景材料保留，不是本项目的攻击对象。

## 决策 2：Goku 与 LlamaGen 不应使用同一套“攻击路径”模板

LlamaGen 的公开路径能具体映射到文本编码器、缓存特征、图像 tokenizer、AR Transformer、训练脚本和公开 checkpoint。Goku 的公开论文则强调图像/视频联合 latent、rectified flow、长序列并行和 checkpoint/容错系统。两者共享训练基础设施概念，但模型数据流不同。

## 决策 3：T5 必须单独建工件谱系

T5 权重、tokenizer、预处理脚本、文本特征缓存和 LlamaGen 主模型 checkpoint 分开编号、分别哈希。不要把缓存目录名称当作模型身份，也不要用模型范数替代哈希。

## 决策 4：先做“可观测现象复现”，不做真实攻击重建

教学实验只使用固定的小型 JSON/CSV 夹具：
- 合成向量：说明内容变化可能与范数相同；
- 合成分片：检查样本覆盖与 rank 间重叠；
- 合成训练日志：标记 loss/grad norm 异常；
- 文件 manifest：建立证据目录的 SHA-256 清单。

不实现 PyTorch 文件替换、真实权重修改、隐藏式触发、后门或作业终止逻辑。

## 决策 5：公开源代码按版本固定，而非“抓 main 当历史”

对 Goku 与 LlamaGen 分别保存访问日期、commit SHA、文件清单和许可证信息。当前 `main` 只作为当前基线；历史事故时间线需要历史 tag/commit 或原始内部材料。
