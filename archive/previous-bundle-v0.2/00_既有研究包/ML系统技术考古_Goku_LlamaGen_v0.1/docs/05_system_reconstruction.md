# 05｜Goku 与 LlamaGen 的系统重建图

## 统一抽象

```text
                         ┌──────────────────────────┐
                         │ 控制面                    │
                         │ Git / review / build      │
                         │ dependency / container    │
                         │ job config / permissions  │
                         └────────────┬─────────────┘
                                      │
                  ┌───────────────────┴───────────────────┐
                  │                                       │
       ┌──────────▼──────────┐                 ┌──────────▼──────────┐
       │ LlamaGen 数据/模型链 │                 │ Goku 数据/模型链    │
       │ images + captions   │                 │ image/video + text  │
       │ VQ tokenizer        │                 │ joint 3D VAE        │
       │ T5 + text features  │                 │ rectified-flow      │
       │ AR Transformer      │                 │ Transformer         │
       └──────────┬──────────┘                 └──────────┬──────────┘
                  │                                       │
                  └───────────────────┬───────────────────┘
                                      ▼
                         ┌──────────────────────────┐
                         │ 执行面                    │
                         │ PyTorch / rank / collectives│
                         │ optimizer / checkpoint   │
                         └────────────┬─────────────┘
                                      ▼
                         ┌──────────────────────────┐
                         │ 证据面                    │
                         │ hashes / configs / logs  │
                         │ artifact provenance      │
                         │ job-rank-node timeline   │
                         └──────────────────────────┘
```

## 关键差别

**LlamaGen**
- 自回归模型把图像 tokenizer 产生的离散图像 token 当作序列目标。
- 文本条件路径涉及 T5 文本编码器及其生成的条件特征。
- 所以必须分别审计 T5 权重、文本特征缓存、图像 tokenizer 与主 AR checkpoint。

**Goku**
- 论文描述的是联合图像/视频生成：图像与视频经 3D 联合 VAE 映射到共享 latent 空间，再由 rectified-flow Transformer 建模。
- 论文公开的大规模训练系统涉及数据筛选、长序列、并行策略、checkpoint 与容错。
- 不能因为 LlamaGen 使用 T5，就假定 Goku 的每条输入路径都使用相同 T5 或相同文本缓存；必须按公开代码/论文和历史工件分别确认。

## 可见和不可见的边界

公开可见：论文、项目网页、公开仓库文件、公开模型卡/发布权重、公开 benchmark 结果。

当前不可见或未取得：内部 GitLab 原始对象、事故时的完整代码 checkout、容器镜像 digest、T5/缓存原始副本、job/rank/node 日志、内部 ACL、checkpoint 历史、实际数据 manifest。

研究时将不可见项放入 `unknowns.csv`，不要用虚构的内部目录或员工身份填补证据空白。
