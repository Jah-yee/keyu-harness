"""Workbench publishing helpers (roadmap P2 兑现): render the source ledger to
markdown, and diff two pinned tree manifests.

- `render_refs(source_registry_csv, out_md)` — 把来源账本渲染成参考文献页
  （docs/references.md 的生成器；此前是手工渲染，会腐化——现在命令化）。
- `diff_manifests(manifest_a, manifest_b)` — 两个 pin 的全树 manifest 对比：
  added / removed / changed（roadmap P2 的"文件树 diff"承诺）。
两者均为纯标准库、离线、确定性。
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROLE_ZH = {
    "INCIDENT_MATERIALS_PAGE": "事件材料页", "SECONDARY_REPORT": "二手报道/访谈",
    "STATEMENT_REPRINT": "声明转载", "PUBLIC_SOFTWARE_REPOSITORY": "公开仓库",
    "RESEARCH_PAPER": "论文", "PUBLIC_MODEL_CONFIG": "模型配置",
    "VERSION_REFERENCE": "版本基线", "SOFTWARE_CITATION_GUIDANCE": "引用规范",
    "RESEARCH_REPRODUCIBILITY_GUIDANCE": "可复现性规范", "TECHNICAL_REFERENCE": "技术参照",
}


def render_refs(source_registry_csv: Path, out_md: Path, *, title: str = "参考文献 References（全量来源账本渲染页）") -> dict:
    """把 source_registry.csv 渲染为 markdown 参考文献页。返回统计。"""
    source_registry_csv = Path(source_registry_csv)
    with source_registry_csv.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    lines = [
        f"# {title}",
        "",
        f"由 `references/source_registry.csv`（{len(rows)} 条）经 `keyu-harness render-refs` 渲染；"
        "任何更新以 CSV 为真源，本页为派生视图。",
        "",
        "状态词汇：LINK_ONLY=仅链接；PAGE_REVIEWED=已在线审阅；CAPTURED=已捕获存档"
        "（SHA-256 见 `evidence/raw/capture_manifest.json`）；NOT_REVIEWED=未审阅。",
        "",
    ]
    for r in rows:
        lines.append(f"### {r['source_id']} · {r['title']}")
        lines.append("")
        lines.append(f"- **创作者/媒体**：{r['creator'] or '—'}")
        lines.append(f"- **类型/角色**：{r['source_type']}（{ROLE_ZH.get(r['source_role'], r['source_role'])}）")
        lines.append(f"- **日期**：{r['publication_date'] or '—'}｜**链接**：{r['url'] or '—'}")
        lines.append(f"- **审阅/取得状态**：{r['review_status']} / {r['capture_status']}")
        extra = []
        if r.get("version_or_commit"):
            extra.append(f"版本：`{r['version_or_commit']}`")
        if r.get("sha256"):
            extra.append(f"SHA-256：`{r['sha256'][:16]}…`")
        if r.get("local_path"):
            extra.append(f"存档：`{r['local_path']}`")
        if extra:
            lines.append(f"- **{'｜'.join(extra)}**")
        lines.append(f"- **支持什么**：{r['what_it_supports'] or '—'}")
        lines.append(f"- **局限**：{r['limits'] or '—'}")
        lines.append("")
    out_md = Path(out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines), encoding="utf-8")
    return {"sources": len(rows), "out": str(out_md)}


def diff_manifests(manifest_a: Path, manifest_b: Path) -> dict:
    """对比两个 pin 的全树 manifest：added / removed / changed（按 path，按 sha256）。"""
    ma = {f["path"]: f["sha256"] for f in _json_load(manifest_a)["files"]}
    mb = {f["path"]: f["sha256"] for f in _json_load(manifest_b)["files"]}
    return {
        "added": sorted(set(mb) - set(ma)),
        "removed": sorted(set(ma) - set(mb)),
        "changed": sorted(p for p in set(ma) & set(mb) if ma[p] != mb[p]),
    }


def _json_load(path: Path) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
