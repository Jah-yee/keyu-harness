# 源码审计：LlamaGen 与 Goku 的公开代码层（Phase H，2026-10-29）

**性质**：对 pinned 树（`evidence/raw/llamagen@{5a50452d,ce98ec41}`、`goku@e29a217b`）的源码级审计——兑现 research_roadmap P1（LlamaGen 源码审计 / Goku 依赖基线）的剩余承诺。全部 E1 级（捕获件离线可验），推断处标注 H。

## 一、LlamaGen：调用图与 T5 缓存生产流

### 1.1 调用图（roadmap P1 承诺，锚点全部来自 pinned 树）

```text
文本 caption
  → language/extract_t5_feature.py        # 缓存生产者：Dataset + T5Embedder
      → language/t5.py T5Embedder         # T5EncoderModel.from_pretrained(path)
      → args.t5_model_path/<t5_model_type>/  # 本地缓存目录（local_cache=True）
  → *.npy 逐 caption 落盘                  # "文本特征缓存"的实体形态
      → autoregressive/train/train_t2i.py  # 缓存消费者：--t5-feat-path 必填参数
          → DDP（torch.nn.parallel.DistributedDataParallel）
          → global_seed × world_size + rank 播种
  → autoregressive/sample/sample_t2i.py / sample_t2i_ddp.py   # 采样入口
```

关键锚点：`extract_t5_feature.py:96` 变量 `t5_xxl = T5Embedder(...)`；`:108` `np.save(...{code_name}.npy)`；`train_t2i.py:229` `--t5-feat-path`（缓存消费的必填参数）。

### 1.2 三列对比（roadmap P1 要求的三列）

| 列 | 状态 |
|---|---|
| 当前公开版本 | HEAD `ce98ec41`（2024-06-29），已 pin + 全树哈希 |
| 最接近事件时间的公开版本 | first commit `5a50452d`（2024-06-10 "code init"）——**公开史只有这 19 天** |
| 事件材料报告的内部版本 | 未知（U01：2024-03 内部 checkout 无公开对应物） |

### 1.3 树 diff（first → HEAD，19 天）

新增 5（全部 HF 发布链路：`gpt_hf.py`、`vq_model_hf.py`、`push_*_to_hf.py`、fake_json）、修改 5（README.md、serve/gpt_model.py 等）、删除 0。**`language/` 三件套（README/t5.py/extract_t5_feature.py）在两个 pin 逐字一致**。

### 1.4 发现一：T5 身份的"公开代码内二相性"（U02 格局改写）

公开代码里有**三层互相独立的 T5 表述**：

| 层 | 表述 | 出处 |
|---|---|---|
| 文档层 | "Download **flan-t5-xl** … into `./pretrained_models/t5-ckpt/`" | language/README.md:14，**两个 pin 逐字一致**（C02 升级：范围限制从"当前 README"收窄为"公开史全程稳定"） |
| 代码层（生产者） | 变量名 `t5_xxl`；实际模型 = **CLI 参数** `args.t5_model_type` | extract_t5_feature.py:96-100 |
| 代码层（菜单） | `available_models = ['t5-v1_1-xxl', 't5-v1_1-xl', 'flan-t5-xl']` | t5.py:16 |

**事件页的 "flan-t5-xxl" 在公开代码菜单中不存在。** 菜单混装两个家族（DeepFloyd `t5-v1_1-*` 与 Google `flan-*`），且 xxl 选项是 `t5-v1_1-xxl` 而非 flan 系。

### 1.5 发现二：未知名字的静默回退（H 级，代码行为实测）

t5.py 的 else 分支：当 `dir_or_name` 不在菜单且非 local_cache 时，`cache_dir` **静默回退到 `t5-v1_1-xxl`** 路径——请求 `flan-t5-xxl` 会静默加载 t5-v1_1-xxl 缓存目录的内容。这是"文档、代码、缓存目录三者身份可以不一致"的具体机制（H：基于公开代码的路径推演，未运行）。

### 1.6 发现三：下载器硬编码两分片假设

t5.py 的 hub 下载列表硬编码 `pytorch_model-00001-of-00002.bin / 00002-of-00002.bin`——与捕获的 flan-t5-**xl** index（2 分片）吻合；而 flan-t5-**xxl** 是 5 分片（本仓库捕获其 index 证实）→ **hub 下载路径对 xxl 形态会断**。README 教你下的 xl + 代码假设的 2 分片 = 文档与代码同为 xl 形态；xxl 只在变量名和菜单里出现。

### 1.7 对 U02 的收敛

公开工件证据链现为四层：README（xl，史稳）→ 缓存生产者变量名（xxl 修辞）→ 模型菜单（无 flan-t5-xxl）→ 分片/维度指纹（xl=2 分片 11.93GB d_model 2048；xxl=5 分片 45.59GB d_model 4096）。**任何未来披露的截图/清单/张量形状，只要含分片数、文件名或 hidden dim 之一，即可即时裁决 xl/xxl**。事件页的 xxl 口径与公开代码的 xl 形态的矛盾，现在有了机制性解释的候选（H：README 教的是 xl 缓存，代码按 CLI 加载，"xxl"可能是修辞或另一条未公开路径）——保持 UNRESOLVED 但可证伪规则已完备。

## 二、Goku：8 文件骨架审计

- 清单：README、`configs/goku_{2b,8b}.yaml`、`goku/model.py`（12KB 模型定义）、`requirements.txt`、`tools/download_flan_t5.py`。
- **维度一致性（P0-b 兑现）**：两份 config 的 `cross_attention_dim: 2048` 与 **flan-t5-xl 的 d_model=2048 一致**（xxl 应为 4096）——公开 Goku 架构与 xl 文本条件器在维度上自洽（C36）。
- **公开材料未见**（roadmap P1 要求显式登记）：训练循环、数据管线、分布式启动器、容错/恢复、文本特征缓存生产脚本——均不在 8 文件中。骨架性质与 C11（requirements 仅为推理/采样依赖）互证。

## 三、对账回执（roadmap P0/P1 清欠）

| roadmap 承诺 | 状态 |
|---|---|
| P0 基线固定（commit/哈希/许可/manifest） | ✅ Phase B（MIT 许可证在案；行号级锚点在引用处标注） |
| P0-b T5 配置+张量形状一致性 | ✅ 本轮（config 指纹 + index 指纹 + 分片数判别；权重本体 GB 级不捕获，登记 unknown） |
| P1 LlamaGen 调用图 + 三列对比 | ✅ 本文 §一 |
| P1 Goku 依赖基线 + "公开材料未见" | ✅ 本文 §二 |
| P1 PyTorch 正常行为矩阵 | ✅ [10_pytorch_matrix.md](10_pytorch_matrix.md) |
| P2 树 diff | ✅ 本文 §1.3（first→HEAD diff；跨 run 隔离由 Phase F 兑现） |


## 四、Goku model.py 审计（四家族最后一件未读工件）

`goku/model.py`（12KB）为 DiT 风格 rectified-flow 视频模型定义：PatchEmbed / AdaLayerNorm / RMSNorm / rotary embedding / Attention（`q_dim, kv_dim` 分离 + `cross_attention` 开关）。**文本条件器不在 model.py 内**——它以 `kv_dim`/`cross_attention` 参数在实例化时注入，数值来自 config 的 `cross_attention_dim: 2048`。公开工件链由此完整闭合：`download_flan_t5.py`（拉 flan-t5-xl）→ `configs/*.yaml`（cross_attention_dim=2048）→ `model.py`（kv_dim 消费）——**三层自洽，且唯一**（C36 复核）。

## 五、LlamaGen 官方种子架构与 caption 预处理（补案例档案 04 的对照面）

- **双种子系统**：`train_t2i.py:35` `seed = args.global_seed * dist.get_world_size() + rank; torch.manual_seed(seed)`——模型/增广 RNG 按 rank 相异；而数据顺序由 DistributedSampler 的 `seed+epoch` 全局统一。S01 卡片 4 的补丁攻击的是**第二套系统**（数据顺序），第一套（按 rank 相异的 torch 种子）是官方设计——这解释了"各 rank 增广不同属正常，数据顺序不同属异常"的检测边界。
- **caption 预处理**：`t5.py:58-85` `get_text_embeddings → text_preprocessing → clean_caption(text)` **连续两次**，注释明言 "The exact text cleaning as was in the training stage"；`bad_punct_regex` 清洗特殊符号；依赖 BeautifulSoup。缓存 `.npy` 的语义 = **清洗后 caption** 经 T5Encoder 的编码——缓存谱系模板因此需要"预处理版本"字段。
- **维度锚点**：`autoregressive/models/gpt.py:42` `caption_dim: int = 2048`——AR 模型的文本条件维度写在公开代码里。

## 六、菜单兼容性裁决（U02 升格）

对照 gpt.py `caption_dim=2048`，T5Embedder 菜单与相关家族的裁决表（全部 E1 捕获件）：

| 模型 | d_model | 在菜单？ | 分片 | 维度兼容 caption_dim=2048 |
|---|---|---|---|---|
| flan-t5-xl | 2048 | ✓（README 路径） | 2 | **✓ 唯一兼容** |
| flan-t5-xxl | 4096 | ✗ 不在菜单 | 5 | ✗ |
| t5-v1_1-xxl | 4096 | ✓（菜单首位） | — | ✗ |
| t5-v1_1-xl | 未捕获 | ✓（菜单） | — | 未决（HTTP 401 门控） |

**结论（C38）**：在公开代码自身的坐标系内（caption_dim=2048），T5Embedder 菜单与相关家族中**唯一维度自洽的选择是 flan-t5-xl**；事件页口径 "flan-t5-xxl" 面临三重不一致（不在菜单 / 维度 4096 / 五分片）。历史运行若真用了 xxl 系，必须存在公开证据之外的代码改动（更换 caption_dim、加投影层、或另一套加载器）——该可能性保持登记（H），但公开工件层现在**内部唯一自洽**。U02 由"未解决"升格为"公开代码内已裁决，内部环境形态仍待原始证据"。
