# 引用与来源管理

## 采用什么引用方式

本项目面向机器学习系统、软件工程和研究工件。书目与引用应优先遵循 FORCE11 的软件引用原则：明确创建者、软件名称、可解析标识符，并尽可能给出版本、日期和发布方。若投稿目标有明确格式，应以目标期刊或会议规范为准；没有指定格式时，可使用常见的数字编号技术引用方式，并用 BibTeX 管理书目元数据。[S14][S15]

对可复现的源码研究，引用不应只指向仓库首页。应尽可能指向 tag、commit 或文件的固定版本，并在分析记录中保留路径、行号、文件哈希和获取状态。提交 SHA 与文件 SHA-256 是不同字段，不能互相替代。

## 引用粒度

### 论文
作者、出版版本中的原始标题、出版物或预印本、年份、DOI / arXiv ID、URL。

### 软件仓库
维护者、项目名称、tag 或 commit、release 日期（若有）、URL、获取日期与许可。若没有持久化存档，仓库 URL 与 commit 仍比只引用 `main` 更具体。

### 源码文件
来源编号、仓库、commit、相对路径、行号或 diff 范围、文件 SHA-256（仅在真实取得文件后填写）、所支持的具体描述与局限。

### 模型与数据工件
模型 ID、revision、config/tokenizer/weight 文件哈希、生产者、消费者任务、获取条件与许可。文件名不等于身份，能被加载也不等于来源已验证。

### 网页报道
保留原始标题、作者/发布机构、发布日期、URL 和获取日期。转载或联合发布的页面应记录其转载关系，不应把同一篇稿件的多个镜像当作独立交叉验证。

## 中文材料

中文标题保留原题。若有必要，可在 `title_translation` 字段填写明确标记的工作译名；工作译名不是正式标题。作者署名和发布日期未能核实的，应明确留空或标记待核实。

## 来源表、主张表和工件表的分工

- `source_registry.csv` 记录材料是什么、来自哪里、目前是否审阅/取得。
- `claim_ledger.csv` 记录具体陈述获得什么程度的支持、还缺什么材料。
- `artifact_registry.csv` 记录代码快照、配置、模型工件、环境记录等对象及其谱系。
- `bibliography.bib` 提供可复用的书目元数据。

这几张表不能合并成一个“可靠度分数”。一篇官方 README 对“README 写了什么”是直接来源，却未必能证明某个历史训练任务使用了对应代码。材料类型、来源独立性、取得状态和主张支持关系应分别记录。

## 方法参考

- [S14] Smith, A. M., Katz, D. S., Niemeyer, K. E., & FORCE11 Software Citation Working Group. (2016). *Software Citation Principles*. PeerJ Computer Science, 2, e86. https://doi.org/10.7717/peerj-cs.86
- [S15] FORCE11 Software Citation Implementation Working Group. *Software Citation Checklist for Developers*. https://github.com/force11/force11-sciwg/blob/master/guidance/software_citation_checklist_for_developers.md
- [S16] ACM Multimedia Systems 2024. *Artifact Review and Badging / Reproducibility Guidance*. https://2024.acmmmsys.org/participation/reproducibility/
