# 虚构组织与环境规格（全部 FICTIONAL，锚点见方括号）

## 1. 虚构组织表

| 占位符 | 角色 | 项目 | 规模 | 锚点 |
|---|---|---|---|---|
| intern-V | 实习生（2021 年起，案发时第 3 年） | VAR T2I 扩展、tokenizer ×2 | 千卡级（自述展示规模） | [REPORTED-BASIS: LP 人物背景/千卡 VAR] |
| intern-C | 实习生（2024-03 下旬入职） | Goku 文生视频（从零写训练代码） | 与 VAR 共池、无配额 | [REPORTED-BASIS: LP] |
| researcher-L | 研究员 | LlamaGen（<100 卡自回归 T2I） | 小规模 | [REPORTED-BASIS: LP] |
| researcher-G | 研究员（后期加入） | Goku 数据/算法 | — | [REPORTED-BASIS: LP] |
| lead-V / lead-C | 两名实习生的直属领导 | 资源协调、停任务权限 | — | [REPORTED-BASIS: LP；**身份不推断**] |
| infra-oncall | Infra 支持与排障 | 压测、异常机剔除机制 | 上百人排障群 | [REPORTED-BASIS: LP] |
| 竞争队 α/β | 同公司其他视频生成团队 | PixelDance/Seaweed 占位 | — | [REPORTED-BASIS: LP，占位化] |

## 2. 虚构集群与作业规格

```text
[FICTIONAL] 集群 genai-pool-07
  调度: trial id = trial-<YYYYMMDD>-<seq>；节点 = node-<2位机房>-<3位序号>
  作业单元: 1 trial × N node × M rank（每 rank 一进程，PyTorch DDP 风格）
  容器: registry.internal/genai-train:2024.06-py39   ← py39 为教学填充，映射 H-FN-1 假设
  恢复策略: robust-training=true（中断后机器保持分配，重启不重拉镜像）
           [REPORTED-BASIS: S01a issues #10 + MegaScale 论文机制]
  确定性装置: det-harness（16 位小数逐位复现校验，覆盖数据读序/算子/通信顺序）
           [REPORTED-BASIS: LP "小数点后16位"]

[FICTIONAL] 共享存储 /mnt/share/genai/
  datasets/          原始数据与标注
  feature_cache/t5/  预提取 T5 文本特征（跨项目复用）[REPORTED-BASIS: S01 3月攻击面]
  checkpoints/       作业输出
  logs/              作业日志汇 collect 目录 [REPORTED-BASIS: LP 日志内藏码位置类型]
  users/<uid>/       个人目录（组内互写开启）[REPORTED-BASIS: S01 共享互写叙述]
  barrier_vgpt/      虚构的作业间步进目录（名字取自被报道字符串，用途为教学演示）
```

## 3. 虚构的一次"带病"作业参数（教学填充）

```yaml
job: trial-20240617-014        # FICTIONAL
nodes: 8   ranks_per_node: 8  # FICTIONAL
sampler_seed: "epoch+seed (预期) / time_ns (展品A注入)"
optimizer: adamw (lr=1e-4)     # FICTIONAL
clip_grad_norm: 1.0            # 展品B注入后实际缩放系数=2
logging: stdout→/mnt/share/genai/logs/trial-20240617-014/  # 展品C注入删行
```

**再次声明**：以上所有具体值（集群名、id 格式、lr、路径）均为虚构；只有方括号标注的机制锚点对应被报道材料。
