# ML Systems Archaeology：Goku × LlamaGen

**版本：0.1｜研究型教学仓库｜更新时间：2026-10-26**

本仓库不是攻击工具，而是一个“机器学习系统技术考古”工作台：用公开论文、公开源码、公开模型卡与事件材料，重建可验证的技术边界；用合成小数据演示工件完整性、采样分片、训练日志和来源追踪的审计方法。

## 研究范围

- **主要对象 A：LlamaGen** — 公开的自回归图像生成研究仓库、文本条件生成路径、T5 与文本特征缓存的工件链。
- **主要对象 B：Goku** — 公开论文、项目页面和 GitHub 仓库；区分公开模型描述、公开代码范围与没有公开的训练工件。
- **关联层：T5 / tokenizer / cached text features / checkpoint / PyTorch runtime / distributed jobs**。
- **排除项：VAR、PixArt 不作为本仓库的攻击对象分析范围。**
- **PyTorch：作为执行层和正常行为参照，不把它当成唯一目标。**

## 研究方法

1. 固定来源与时间基线。
2. 将每个说法拆成“主张—来源—支持范围—限制—待验证工件”。
3. 把论文描述与真实公开仓库文件结构分别记录。
4. 只在合成数据上演示可观测现象，不修改真实模型权重、不替换 PyTorch 文件、不注入持久化机制、不终止真实作业。
5. 每个结论都保留证据等级和不确定性。

## 快速运行

只依赖 Python 标准库：

```bash
python scripts/run_all.py
python -m unittest discover -s tests -v
```

单独运行：

```bash
python -m src.ml_archaeology.audit_toy_vectors fixtures/toy_t5_vectors.json
python -m src.ml_archaeology.audit_sampler_partitions fixtures/sampler_partitions.json
python -m src.ml_archaeology.audit_training_trace fixtures/synthetic_training_trace.csv
python -m src.ml_archaeology.manifest fixtures
```

## 目录结构

```text
docs/
  00_scope_and_method.md
  01_goku_public_release_audit.md
  02_llamagen_public_release_audit.md
  03_t5_model_id_discrepancy.md
  04_event_claims_and_evidence.md
  05_system_reconstruction.md
  06_unobserved_artifacts.md
references/
  source_registry.csv
fixtures/
  toy_t5_vectors.json
  sampler_partitions.json
  synthetic_training_trace.csv
src/ml_archaeology/
  audit_toy_vectors.py
  audit_sampler_partitions.py
  audit_training_trace.py
  manifest.py
tests/
scripts/
```

## 重要限制

- 本仓库没有内部 GitLab 原始 commit、涉事 Docker 镜像、真实 T5 文件、内部共享存储日志或完整训练 trace。
- Goku 的论文指标不能代替涉事训练作业的日志；公开模型权重也不能自动代表 2024 年当时的权重。
- 事件整理页展示的代码摘录是公开文章中的材料，不等于外部已独立保全的原始 Git 对象或镜像。
- 合成夹具是教学样本，不是实际攻击代码，也不代表真实事件的精确实现。
