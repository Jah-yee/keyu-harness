# T5 载体风险面（U10 推进，2026-10-29）

**性质**：U10（T5 载体实现）的分析文档——把"权重文件 / 加载钩子 / 序列化机制"三种可能性的公开风险面铺开，为将来原始证据出现时的快速裁决做准备。全部为公开代码分析（H 级推断已标注），不包含攻击实现。

## 三种载体的判别特征

| 假设 | 机制 | 需要的原始证据 | 公开侧佐证 |
|---|---|---|---|
| 权重文件本体被改 | 修改 .bin/.safetensors 内的张量或附加 pickle 流 | 原始权重哈希 + 逐 tensor 对比 | LatePost "类似一个压缩包" <sup>[S10]</sup> |
| 加载钩子 | 修改 transformers 的加载函数或 from_pretrained 路径 | transformers 库 diff | LlamaGen language/t5.py 用 T5EncoderModel.from_pretrained |
| 序列化机制滥用 | torch.load 的 pickle 反序列化执行任意代码 | 反序列化调用栈 | PyTorch v2.6.0 release notes 反序列化漏洞修复（issues 评论引用） |

## 三个已确证的相关事实（E1）

1. LlamaGen 缓存生产者把 **T5EncoderModel.from_pretrained(path)** 的输出逐 caption 存为 `.npy`——消费方 `train_t2i.py --t5-feat-path` 只读 `.npy`，**不直接触碰权重**。这意味着：篡改权重影响的是"缓存再生成"，而已生成的缓存不受权重篡改影响——**攻击缓存比攻击权重更高效**（与事件页"篡改 T5 权重导致 LlamaGen 无法正常 work"的表述存在张力，登记 H）。
2. t5.py 的 T5Embedder 菜单不包含 flan-t5-xxl，未知名字静默回退到 t5-v1_1-xxl 缓存目录（C34）。
3. `nonan` 卡片证明加载路径上存在可执行上下文（nan_to_num_ 在 checkpoint 加载时运行）——**这意味着加载路径被 hook 过是既成事实**（REPORTED），三假设中的"钩子"假设有直接行为证据。

## 防御要点（从特性 07/00 检测配方延伸）

- 加载前逐文件哈希 vs 登记清单（缓存谱系的第零道门）
- safetensors 优先，拒绝不可信 pickle（v2.6.0 反序列化修复是分水岭）
- 加载路径代码审计：from_pretrained/torch.load 周边无业务外改动
- 消费方与生产方的**缓存谱系登记**：producer revision + 输入版本 + 哈希 + 消费 job ID

## 对 U10 的推进

U10 从"未推进"升格为"三假设已结构化 + 判别证据清单已定义"。剩余工作需要原始工件（权重哈希/加载调用栈），公开渠道不可满足——登记冻结，与 U01 同类。
