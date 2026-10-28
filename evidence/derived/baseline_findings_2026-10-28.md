# 基线固定调研笔记（Phase B，2026-10-28）

**性质**：E1 级发现（全部可由本目录捕获工件离线复验）。本笔记修正一处早期记录，并裁决两项未知项。

## 1. LlamaGen commit 考古：仓库史只有 16 天（U01 裁决）

- 公开仓库全部历史 = **16 个 commit**，起于 **2024-06-10 20:31 UTC（`5a50452db7…` "code init"）**，止于 **2024-06-29 20:38 UTC（`ce98ec4180…`）**。
- **修正**：早期记录"main 冻结于 2024-08-15"系 `pushed_at` 元数据误读——最后 commit 实为 06-29。
- **U01 裁决（C30，DIRECTLY_SUPPORTED）**：2024-03 的内部 checkout 在公开渠道**没有对应物**——公开仓库诞生晚于攻击窗口开端（2024-03）。该未知项在公开渠道内不可满足，除非出现泄露或司法材料。对复刻计划的影响：2024-03 相关特性的保真度上限为 F2（功能对齐）。
- 两端点已 pin + 全树哈希：`evidence/raw/llamagen@5a50452d`（105 文件）、`evidence/raw/llamagen@ce98ec41`（110 文件）。
- GitHub releases 为空：模型发布在 Hugging Face（FoundationVision/LlamaGen 模型页），不在 GitHub Releases。

## 2. Goku 公开仓库 = 模型定义骨架（U02 天平更新）

- `Saiyan-World/goku@e29a217b`（2025-02-19）仅 **8 文件 / 20KB**：README、两份 config（goku_2b/8b.yaml）、`goku/model.py`（12KB 模型定义）、requirements.txt、**`tools/download_flan_t5.py`**。
- **该下载脚本拉取 `google/flan-t5-xl`**（含 generation_config、两份 safetensors shard、spiece.model 等 9 文件，并注明"recommend using the *.safetensors files for safety reasons"）。
- **U02 天平更新（C31，DIRECTLY_SUPPORTED）**：公开工件指向 **xl 的有两处**（LlamaGen README + Goku 下载器），指向 **xxl 的仅事件页一处**。仍不能裁决 2024-03 内部状态，但公开侧证据一致偏向 xl。
- requirements.txt 证实账本 C11（diffusers==0.32.2 / transformers==4.48.0 / av==12.0.0）。

## 3. 调用点计数 = 版本指纹（C32，DIRECTLY_SUPPORTED）

对捕获的三个 tag 快照离线复检 `_rank_not_in_group(`：**v2.2.0=28、v2.3.0=29、v2.4.0=31**（`_rank_not_in_this_group` 均为 0）。含义：

1. E1 发现现在**离线可复现**（不再依赖网络）；
2. `_rank_not_in_group` 的调用点计数随版本变化——**若未来出现被改的 distributed_c10d.py，按调用点计数即可为版本断代**；
3. 主 README/案例 03 中"31 个调用点"的表述精确化为 v2.4.0 口径。

## 4. 捕获清单与哈希

| 快照 | commit/rev | 文件数 | 字节 | 状态 |
|---|---|---|---|---|
| llamagen@5a50452d | 5a50452db783a1351073a42eab4cac4eda80f618 | 105 | 7,384,620 | CAPTURED（全树哈希 100% 复验） |
| llamagen@ce98ec41 | ce98ec41803a74a90ce68c40ababa9eaeffeb4ec | 110 | 7,396,681 | CAPTURED（同上） |
| goku@e29a217b | e29a217bdb9195fa26b2db6add9f1848472a1bf9 | 8 | 19,855 | CAPTURED |
| pytorch/v2.2.0 · v2.3.0 · v2.4.0 | 8ac9b20d… / 97ff6cfd… / d990dada… | 5×3 | — | CAPTURED（sidecar manifest） |
| flan-t5-xl@efd6532 · flan-t5-xxl@d2dd233 | efd6532 / d2dd233 | 4×2 | — | CAPTURED（config+tokenizer+spiece） |

复核记录：tarball 223/223 + sidecar 23/23 哈希复验一致（2026-10-28）。账本联动：artifact_registry 9 行、source_registry 13 行升级 CAPTURED（哈希/路径/revision 齐备），新增主张 C30–C32，未知项 U01/U02 更新。

## 5. 对复刻计划（Phase C–F）的输入

- 玩具训练环的"真实采样器行为"对照物 = `evidence/raw/pytorch/<tag>/distributed.py`（离线可得）。
- 特性 01–04 的 F0 复现以捕获文件为基线源，不再引用网络。
- LlamaGen 公开调用图审计（研究路线 P1）可直接在 pinned 树上进行。
