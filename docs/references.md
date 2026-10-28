# 参考文献 References（全量来源账本渲染页）

由 `references/source_registry.csv`（34 条）经 `keyu-harness render-refs` 渲染；任何更新以 CSV 为真源，本页为派生视图。

状态词汇：LINK_ONLY=仅链接；PAGE_REVIEWED=已在线审阅；CAPTURED=已捕获存档（SHA-256 见 `evidence/raw/capture_manifest.json`）；NOT_REVIEWED=未审阅。

### S01 · 2024 年字节跳动前实习生田柯宇 (Tian Keyu) 模型训练攻击事件：受害者陈述与证据整理

- **创作者/媒体**：Page author/byline not verified in the current capture
- **类型/角色**：incident_materials_page（事件材料页）
- **日期**：2026-10-12｜**链接**：https://keyu-tian-sabotage.github.io/
- **审阅/取得状态**：PAGE_REVIEWED / HASHED
- **版本：`e4292f48b3ad (repo pinned; tree manifest in evidence/raw/s01_repo@e4292f48/manifest.json)`｜SHA-256：`320dbeab50f94e6f…`｜存档：`evidence/raw/s01_page/s01_page.html`**
- **支持什么**：The contents and claims presented on this incident-materials page, including its timeline and displayed excerpts
- **局限**：The page is not an independently preserved internal Git object, package image, job log, or original artifact bundle; displayed excerpts do not by themselves establish runtime provenance.

### S02 · LlamaGen official repository

- **创作者/媒体**：FoundationVision
- **类型/角色**：software_repository（公开仓库）
- **日期**：—｜**链接**：https://github.com/FoundationVision/LlamaGen
- **审阅/取得状态**：PAGE_REVIEWED / LINK_ONLY
- **支持什么**：Current public LlamaGen repository structure, README statements, published sample entry points, and release notes
- **局限**：Current main is mutable and post-dates the reported March 2024 window; this repository has not been captured locally in this bundle.

### S03 · Autoregressive Model Beats Diffusion: Llama for Scalable Image Generation

- **创作者/媒体**：Peize Sun et al.
- **类型/角色**：preprint（论文）
- **日期**：2024-06｜**链接**：https://arxiv.org/abs/2406.06525
- **审阅/取得状态**：PAGE_REVIEWED / LINK_ONLY
- **支持什么**：The paper's published method and stated results
- **局限**：A paper does not establish which source revision, weights, cache, or runtime a particular historical job loaded.

### S04 · LlamaGen language README

- **创作者/媒体**：FoundationVision
- **类型/角色**：repository_documentation（公开仓库）
- **日期**：—｜**链接**：https://github.com/FoundationVision/LlamaGen/blob/main/language/README.md
- **审阅/取得状态**：PAGE_REVIEWED / LINK_ONLY
- **支持什么**：Current public LlamaGen language README and its documented FLAN-T5-XL setup
- **局限**：Current README is not proof of the model revision used by a historical job.

### S05 · Goku official repository

- **创作者/媒体**：Saiyan-World
- **类型/角色**：software_repository（公开仓库）
- **日期**：—｜**链接**：https://github.com/Saiyan-World/goku
- **审阅/取得状态**：PAGE_REVIEWED / LINK_ONLY
- **支持什么**：Current public Goku repository layout and its published README
- **局限**：The current public repository is a later release and is not direct evidence of 2024 internal source state.

### S06 · Goku: Flow Based Video Generative Foundation Models

- **创作者/媒体**：Shoufa Chen et al.
- **类型/角色**：preprint（论文）
- **日期**：2025-02-07｜**链接**：https://arxiv.org/abs/2502.04896
- **审阅/取得状态**：PAGE_REVIEWED / LINK_ONLY
- **支持什么**：The public 2025 Goku paper and its published architecture description
- **局限**：The paper post-dates the reported 2024 events and cannot independently establish incident-time implementation details.

### S07 · PyTorch Versions

- **创作者/媒体**：PyTorch Contributors
- **类型/角色**：version_documentation（版本基线）
- **日期**：—｜**链接**：https://github.com/pytorch/pytorch/wiki/PyTorch-Versions
- **审阅/取得状态**：NOT_REVIEWED / LINK_ONLY
- **支持什么**：PyTorch version/release reference material
- **局限**：Release history does not identify the package installed in any specific historical environment.

### S08 · google/flan-t5-xl config.json

- **创作者/媒体**：Google / Hugging Face model repository
- **类型/角色**：model_configuration（模型配置）
- **日期**：—｜**链接**：https://huggingface.co/google/flan-t5-xl/blob/efd6532/config.json
- **审阅/取得状态**：PAGE_REVIEWED / REVISION_IDENTIFIED
- **版本：`efd6532`**
- **支持什么**：The configuration fields displayed for the reviewed FLAN-T5-XL config revision
- **局限**：The current config is not proof of the historical weights or tokenizer loaded by a training job.

### S09 · google/flan-t5-xxl config.json

- **创作者/媒体**：Google / Hugging Face model repository
- **类型/角色**：model_configuration（模型配置）
- **日期**：—｜**链接**：https://huggingface.co/google/flan-t5-xxl/blob/d2dd233/config.json
- **审阅/取得状态**：PAGE_REVIEWED / REVISION_IDENTIFIED
- **版本：`d2dd233`**
- **支持什么**：The configuration fields displayed for the reviewed FLAN-T5-XXL config revision
- **局限**：The current config is not proof of the historical weights or tokenizer loaded by a training job.

### S10 · 还原田柯宇事件：被破坏的训练，和一个争抢 “天才” 的时代

- **创作者/媒体**：董慧、陈佳惠、管艺雯；编辑：管艺雯（页面署名）
- **类型/角色**：journalistic_investigation（二手报道/访谈）
- **日期**：2026-10-23｜**链接**：https://t.cj.sina.com.cn/articles/view/7294209083/1b2c4cc3b00101x36w
- **审阅/取得状态**：PAGE_REVIEWED / CAPTURED
- **SHA-256：`20da60ec8ced06e0…`｜存档：`evidence/raw/latepost_sina/latepost_page.html`**
- **支持什么**：What the LatePost investigation reports and attributes to interviews, statements, and materials
- **局限**：This is a report republished on Sina; do not count a syndicated copy as an independent corroborating source. Reported claims should be linked to original artifacts where available.

### S11 · PyTorch v2.2.0 source tree

- **创作者/媒体**：PyTorch Contributors
- **类型/角色**：tagged_source_tree（版本基线）
- **日期**：2024-01-30｜**链接**：https://github.com/pytorch/pytorch/tree/v2.2.0
- **审阅/取得状态**：NOT_REVIEWED / CAPTURED
- **版本：`v2.2.0`｜SHA-256：`ca22aa1f88866eef…`｜存档：`evidence/raw/pytorch/v2.2.0`**
- **支持什么**：The tagged public PyTorch v2.2.0 source baseline
- **局限**：Candidate baseline only; does not prove the incident runtime used this version.

### S12 · PyTorch v2.3.0 source tree

- **创作者/媒体**：PyTorch Contributors
- **类型/角色**：tagged_source_tree（版本基线）
- **日期**：2024-04-24｜**链接**：https://github.com/pytorch/pytorch/tree/v2.3.0
- **审阅/取得状态**：NOT_REVIEWED / CAPTURED
- **版本：`v2.3.0`｜SHA-256：`dac708fd1e8e9a22…`｜存档：`evidence/raw/pytorch/v2.3.0`**
- **支持什么**：The tagged public PyTorch v2.3.0 source baseline
- **局限**：Candidate baseline only; does not prove the incident runtime used this version.

### S13 · PyTorch v2.4.0 source tree

- **创作者/媒体**：PyTorch Contributors
- **类型/角色**：tagged_source_tree（版本基线）
- **日期**：2024-07-24｜**链接**：https://github.com/pytorch/pytorch/tree/v2.4.0
- **审阅/取得状态**：NOT_REVIEWED / CAPTURED
- **版本：`v2.4.0`｜SHA-256：`1113156de36b938f…`｜存档：`evidence/raw/pytorch/v2.4.0`**
- **支持什么**：The tagged public PyTorch v2.4.0 source baseline
- **局限**：Candidate baseline only; does not prove the incident runtime used this version.

### S14 · Software Citation Principles

- **创作者/媒体**：Smith, Katz, Niemeyer, and FORCE11 Software Citation Working Group
- **类型/角色**：peer_reviewed_article（引用规范）
- **日期**：2016｜**链接**：https://doi.org/10.7717/peerj-cs.86
- **审阅/取得状态**：PAGE_REVIEWED / LINK_ONLY
- **支持什么**：Principles for citing software with attribution, persistent identification, accessibility, and version specificity
- **局限**：Citation guidance, not evidence about the incident itself.

### S15 · Software Citation Checklist for Developers

- **创作者/媒体**：FORCE11 Software Citation Implementation Working Group
- **类型/角色**：research_software_guidance（引用规范）
- **日期**：2019｜**链接**：https://github.com/force11/force11-sciwg/blob/master/guidance/software_citation_checklist_for_developers.md
- **审阅/取得状态**：PAGE_REVIEWED / LINK_ONLY
- **支持什么**：Practical checklist for making research software releases citable
- **局限**：Software publication guidance, not evidence about the incident itself.

### S16 · Artifact Review and Badging

- **创作者/媒体**：ACM Multimedia Systems 2024 Artifact Evaluation / Reproducibility guidance
- **类型/角色**：research_artifact_guidance（可复现性规范）
- **日期**：2024｜**链接**：https://2024.acmmmsys.org/participation/reproducibility/
- **审阅/取得状态**：PAGE_REVIEWED / LINK_ONLY
- **支持什么**：Guidance that research artifacts should be accessible, runnable, and accompanied by clear reproducibility instructions
- **局限**：Conference-specific artifact guidance; not incident evidence.

### S17 · Goku public requirements.txt

- **创作者/媒体**：Saiyan-World
- **类型/角色**：software_dependency_manifest（公开仓库）
- **日期**：—｜**链接**：https://github.com/Saiyan-World/goku/blob/main/requirements.txt
- **审阅/取得状态**：PAGE_REVIEWED / LINK_ONLY
- **支持什么**：The dependencies declared in the currently reviewed public Goku requirements file, including version pins visible there
- **局限**：Current main is mutable and is not a manifest for a 2024 internal environment.

### S18 · LlamaGen text-conditional sampling entry point

- **创作者/媒体**：FoundationVision
- **类型/角色**：source_code_file（公开仓库）
- **日期**：—｜**链接**：https://github.com/FoundationVision/LlamaGen/blob/main/autoregressive/sample/sample_t2i.py
- **审阅/取得状态**：NOT_REVIEWED / LINK_ONLY
- **支持什么**：A public path referenced by the LlamaGen README as a text-to-image sampling entry point
- **局限**：The exact file contents and revision still need a pinned snapshot before line-level claims are made.

### S19 · LlamaGen class-conditional sampling entry point

- **创作者/媒体**：FoundationVision
- **类型/角色**：source_code_file（公开仓库）
- **日期**：—｜**链接**：https://github.com/FoundationVision/LlamaGen/blob/main/autoregressive/sample/sample_c2i.py
- **审阅/取得状态**：NOT_REVIEWED / LINK_ONLY
- **支持什么**：A public path referenced by the LlamaGen README as a class-conditional sampling entry point
- **局限**：The exact file contents and revision still need a pinned snapshot before line-level claims are made.

### S20 · PyTorch v2.2.0 DistributedSampler source

- **创作者/媒体**：PyTorch Contributors
- **类型/角色**：source_code_file（版本基线）
- **日期**：2024-01-30｜**链接**：https://github.com/pytorch/pytorch/blob/v2.2.0/torch/utils/data/distributed.py
- **审阅/取得状态**：NOT_REVIEWED / CAPTURED
- **版本：`v2.2.0`｜SHA-256：`8fa2c5a8ea7a4a1f…`｜存档：`evidence/raw/pytorch/v2.2.0/distributed.py`**
- **支持什么**：The normal public implementation baseline for distributed sampling at tag v2.2.0
- **局限**：Baseline only; no claim that this file was changed in the historical environment.

### S21 · PyTorch v2.3.0 DistributedSampler source

- **创作者/媒体**：PyTorch Contributors
- **类型/角色**：source_code_file（版本基线）
- **日期**：2024-04-24｜**链接**：https://github.com/pytorch/pytorch/blob/v2.3.0/torch/utils/data/distributed.py
- **审阅/取得状态**：NOT_REVIEWED / CAPTURED
- **版本：`v2.3.0`｜SHA-256：`8fa2c5a8ea7a4a1f…`｜存档：`evidence/raw/pytorch/v2.3.0/distributed.py`**
- **支持什么**：The normal public implementation baseline for distributed sampling at tag v2.3.0
- **局限**：Baseline only; no claim that this file was changed in the historical environment.

### S22 · PyTorch v2.4.0 DistributedSampler source

- **创作者/媒体**：PyTorch Contributors
- **类型/角色**：source_code_file（版本基线）
- **日期**：2024-07-24｜**链接**：https://github.com/pytorch/pytorch/blob/v2.4.0/torch/utils/data/distributed.py
- **审阅/取得状态**：NOT_REVIEWED / CAPTURED
- **版本：`v2.4.0`｜SHA-256：`8fa2c5a8ea7a4a1f…`｜存档：`evidence/raw/pytorch/v2.4.0/distributed.py`**
- **支持什么**：The normal public implementation baseline for distributed sampling at tag v2.4.0
- **局限**：Baseline only; no claim that this file was changed in the historical environment.

### S23 · PyTorch v2.2.0 serialization source

- **创作者/媒体**：PyTorch Contributors
- **类型/角色**：source_code_file（版本基线）
- **日期**：2024-01-30｜**链接**：https://github.com/pytorch/pytorch/blob/v2.2.0/torch/serialization.py
- **审阅/取得状态**：NOT_REVIEWED / CAPTURED
- **版本：`v2.2.0`｜SHA-256：`03a94fb97170a594…`｜存档：`evidence/raw/pytorch/v2.2.0/serialization.py`**
- **支持什么**：The normal public serialization/checkpoint-loading baseline at tag v2.2.0
- **局限**：Baseline only; no claim that this file was changed in the historical environment.

### S24 · 字节跳动回应实习生破坏大模型训练传闻：实习生已辞退

- **创作者/媒体**：北京日报页面转载环球网内容；原始公司声明链接未在该页面中独立固定
- **类型/角色**：organizational_statement_reprint（声明转载）
- **日期**：2024-10-19｜**链接**：https://xinwen.bjd.com.cn/content/s67136cd6e4b0c25b287cf740.html
- **审阅/取得状态**：PAGE_REVIEWED / LINK_ONLY
- **支持什么**：The text of the organizational clarification as reproduced by Beijing Daily / Global Times, including the stated dismissal and the company's qualification of some public claims
- **局限**：A reprinted statement is not the original publishing account; it is evidence of the statement as reported, not independent evidence of all underlying technical details.

### S25 · 字节跳动起诉攻击模型训练的实习生 索赔800万元

- **创作者/媒体**：关聪（财新）
- **类型/角色**：journalistic_legal_reporting（二手报道/访谈）
- **日期**：2024-11-28｜**链接**：https://companies.caixin.com/2024-11-28/102262266.html
- **审阅/取得状态**：PAGE_REVIEWED / LINK_ONLY
- **支持什么**：Caixin's report that ByteDance confirmed the lawsuit had been accepted and described the requested damages and apology
- **局限**：Legal reporting supports what was reported about the filing; it does not provide the internal source code, training logs, or an adjudicated technical finding.

### S26 · ByteDance seeks $1.1 million damages from intern in AI breach case, report says

- **创作者/媒体**：Reuters; page hosted by Investing.com
- **类型/角色**：journalistic_legal_reporting（二手报道/访谈）
- **日期**：2024-11-28｜**链接**：https://www.investing.com/news/stock-market-news/bytedance-seeks-11-million-damages-from-intern-in-ai-breach-case-report-says-3745565
- **审阅/取得状态**：PAGE_REVIEWED / LINK_ONLY
- **支持什么**：Reuters' report of the lawsuit and its attribution to other reporting and company statements
- **局限**：This page is a Reuters story hosted by Investing.com; the article itself attributes part of the case details to Legal Weekly, so it should not automatically be treated as independent of every Chinese-language report.

### S27 · MegaScale: Scaling Large Language Model Training to More Than 10,000 GPUs

- **创作者/媒体**：ByteDance Seed team (Qi Huang et al.)
- **类型/角色**：preprint（论文）
- **日期**：2024-02｜**链接**：https://arxiv.org/abs/2402.15627
- **审阅/取得状态**：PAGE_REVIEWED / LINK_ONLY
- **支持什么**：Publicly documents the robust-training/fault-tolerance mechanism cited in the incident-page clarification for machine stickiness.
- **局限**：2024-02 LLM-training paper; does not describe the video-training cluster or prove its configuration.

### S28 · S01 repository issues #10 and #12 with comments (GitHub API capture)

- **创作者/媒体**：keyu-tian-sabotage page maintainer and commenters
- **类型/角色**：incident_repository_discussion（事件材料页）
- **日期**：2026-10｜**链接**：https://api.github.com/repos/keyu-tian-sabotage/keyu-tian-sabotage.github.io/issues/10/comments
- **审阅/取得状态**：PAGE_REVIEWED / CAPTURED
- **版本：`repo head e4292f48b3ad`｜SHA-256：`ec05f3b5da02b560…`｜存档：`evidence/raw/s01_issues/issue10_comments.json`**
- **支持什么**：Author clarifications: modify_t5 lived in the VAR dev repo without review; PyTorch edited in place on live allocated machines; Robust Training machine stickiness as persistence.
- **局限**：Page-maintainer statements remain single-party; comment threads are community discussion.

### S29 · PingWest: 如果你在训模型时遇到了田柯宇

- **创作者/媒体**：PingWest (品玩)
- **类型/角色**：journalistic_feature（二手报道/访谈）
- **日期**：2026-10｜**链接**：https://www.pingwest.com/a/318482
- **审阅/取得状态**：PAGE_REVIEWED / CAPTURED
- **存档：`evidence/raw/pingwest_article.html`**
- **支持什么**：Third-party retelling of the mechanism excerpts and Issue #10 clarifications; confirms which details circulated publicly.
- **局限**：Shares S01 material; consistency check only, not independent verification.

### S30 · anti-keyu-tian ML-platform fingerprint defense material

- **创作者/媒体**：drscrewdriver (GitHub)
- **类型/角色**：defensive_reference_repo（技术参照）
- **日期**：—｜**链接**：https://github.com/drscrewdriver/anti-keyu-tian
- **审阅/取得状态**：NOT_REVIEWED / LINK_ONLY
- **支持什么**：Third-party defensive reference inspired by the incident, for detection-recipe comparison.
- **局限**：Unreviewed third-party content; inclusion is not endorsement.

### S31 · Huxiu: 田柯宇发誓，说谎会"终生研究受挫"

- **创作者/媒体**：Huxiu (虎嗅)
- **类型/角色**：journalistic_feature（二手报道/访谈）
- **日期**：2026-10｜**链接**：https://www.huxiu.com/article/4897169.html
- **审阅/取得状态**：NOT_REVIEWED / LINK_ONLY
- **支持什么**：Additional narrative-line source for the second coverage wave.
- **局限**：Fetch blocked by anti-scraping; content not yet reviewed; obtain via archive before use.

### S32 · PyTorch v2.4.0 distributed_c10d source

- **创作者/媒体**：PyTorch Contributors
- **类型/角色**：source_code_file（版本基线）
- **日期**：2024-07-24｜**链接**：https://github.com/pytorch/pytorch/blob/v2.4.0/torch/distributed/distributed_c10d.py
- **审阅/取得状态**：PAGE_REVIEWED / CAPTURED
- **版本：`v2.4.0`｜SHA-256：`9192cb6543edfe29…`｜存档：`evidence/raw/pytorch/v2.4.0/distributed_c10d.py`**
- **支持什么**：Baseline verifying _rank_not_in_group (31 call sites) and absence of _rank_not_in_this_group.
- **局限**：Tag-level check only; no link to the historical runtime.

### S33 · elsewhere 播客第 007 期文字版（PANews 转载页）

- **创作者/媒体**：elsewhere别处发生；PANews hosting
- **类型/角色**：interview_transcript（二手报道/访谈）
- **日期**：2026-10-12｜**链接**：https://www.panewslab.com/zh/articles/01a134c9-3896-7790-a987-1f3c8244c84e
- **审阅/取得状态**：PAGE_REVIEWED / CAPTURED
- **SHA-256：`55fce00d1e8f4678…`｜存档：`evidence/raw/panews_interview/panews_page.html`**
- **支持什么**：The subject-of-complaint party narrative: manual stops, GPT-written program, denials.
- **局限**：Body is JS-rendered; key sections extracted; elsewhere later noted pre-publication cross-checking gaps (2026-10-19).

### S34 · PyTorch v2.1.0 source tree (five target files)

- **创作者/媒体**：PyTorch Contributors
- **类型/角色**：tagged_source_tree（版本基线）
- **日期**：2024-01-18｜**链接**：https://github.com/pytorch/pytorch/tree/v2.1.0
- **审阅/取得状态**：PAGE_REVIEWED / CAPTURED
- **版本：`v2.1.0`｜存档：`evidence/raw/pytorch/v2.1.0`**
- **支持什么**：摘录相容性四 tag 口径的最早基线
- **局限**：全树未捕获（仅五目标文件）
