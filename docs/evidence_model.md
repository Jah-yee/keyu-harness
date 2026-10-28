# 证据模型：材料、支持关系与未知项

## 为什么不把来源排成一条简单的“可信度排行榜”

“官方来源”“新闻报道”“源码文件”和“技术推断”不是同一种对象。来源类型不能直接替代主张核验：官方文档对公开 API 的说明可以是直接证据，但对某次历史运行是否加载了该 API，仍然需要运行环境和日志。

因此，项目把三件事分开记录：

1. **来源角色（source_role）**：材料属于哪种来源。
2. **取得与审阅状态（review_status / capture_status）**：我们是否看过网页、固定了版本、实际取得文件并计算哈希。
3. **主张状态（claim status）**：该材料与具体陈述之间是什么支持关系。

这不是给材料或人物打分，而是让读者知道每一条陈述走到了证据链的哪一步。

## 来源角色

- `INCIDENT_MATERIALS_PAGE`：事件材料整理页。能直接证明该页面呈现了什么；不自动证明所展示内部材料已被独立保全。
- `SECONDARY_REPORT`：记者调查或二手报道。记录署名、采访范围、引用对象及转载关系。
- `PUBLIC_SOFTWARE_REPOSITORY`：公开代码仓库或其文件。
- `RESEARCH_PAPER`：论文或预印本。
- `PUBLIC_MODEL_CONFIG`：公开模型配置或模型卡。
- `VERSION_REFERENCE`：明确 tag 的软件基线。
- `SOFTWARE_CITATION_GUIDANCE` / `RESEARCH_REPRODUCIBILITY_GUIDANCE`：引用和工件复现方法参考。

来源角色不是可靠度排序。两个互相转载同一篇文章的网页不构成两份独立证据。

## 取得状态

- `LINK_ONLY`：登记了 URL，尚未本地保存原始材料。
- `REVISION_IDENTIFIED`：有明确 tag、commit 或模型 revision，但本地文件仍未取得。
- `CAPTURED`：原始文件已保存，且记录了本地路径。
- `HASHED`：已取得文件并计算哈希。
- `ARCHIVED`：有明确归档标识和可追溯元数据。

不能因为浏览器打开过网页，就填写本地 `sha256`。不能把上游 commit SHA 写入文件哈希字段。

## 主张状态

- `DIRECTLY_SUPPORTED`：来源直接支持陈述，且陈述范围没有超出来源内容。
- `DIRECTLY_SUPPORTED_WITH_SCOPE_LIMIT`：公开材料直接支持有限范围的陈述，但不能外推到其他时间、环境或对象。
- `CORROBORATED`：有来源独立性可说明的多份材料相互支持。
- `REPORTED_NOT_INDEPENDENTLY_VERIFIED`：某来源确实报告了该内容，但原始工件尚未独立核验。
- `INFERRED`：由公开技术结构推导出的解释，仍需检验。
- `UNRESOLVED`：当前材料不足以判定。
- `CONTRADICTED`：可定位材料之间存在尚未解释的冲突。
- `SIMULATED`：本仓库的合成教学数据。

## 技术因果链

```text
具体代码/工件差异
        |
        v
证据表明目标任务加载了该版本/工件
        |
        v
可观测的运行行为变化
        |
        v
与报告现象的时间关联
        |
        v
可重复的对照测试或修复比较
        |
        v
替代解释被逐项检查
```

缺少中间环节时，不应把源码差异写成已经证实的历史因果。

## 三条核心证据链

### A. LlamaGen / T5 / 文本特征缓存
需要历史源码版本、T5 config 与权重、tokenizer revision、缓存 manifest、缓存生成代码、训练配置、消费者 job 和 checkpoint 元数据。

### B. Goku / 分布式训练
需要同时期代码与配置、容器或环境身份、job/rank/node 日志、checkpoint 元数据，以及公开论文与历史系统之间的对应材料。

### C. 框架源码到运行时
需要仓库 commit、构建产物、容器 digest、依赖清单、实际 import 路径和任务记录。公开 PyTorch tag 只提供正常行为基线。

## 完整性不等于真实性

SHA-256 能用于检查已取得文件的字节是否发生变化；它不能单独证明作者、首次创建时间、动机，或某个任务实际加载了该文件。

## 对未知项的态度

没有取得的内部源码、工件和日志统一登记为未知。虚构的内部目录、负责人关系或示例日志只能出现在清楚标记的教学场景中，不能进入历史证据账本。
