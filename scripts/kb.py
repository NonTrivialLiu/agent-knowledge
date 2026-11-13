#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""agent-knowledge 库维护工具。

用法：
  python3 kb.py lint     # 校验全部条目 frontmatter/文件名/URL 去重，出错退出码 1
  python3 kb.py catalog  # 从 frontmatter 再生各分类 CATALOG.md（手写会被覆盖）
  python3 kb.py stats    # 分类计数

规则见 references/ingest.md。权威元数据是每篇正文头部的 YAML frontmatter，
CATALOG.md 与本脚本输出都是派生视图。
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFS = ROOT / "references"
CLASSES = [p.name for p in REFS.iterdir() if p.is_dir()]
REQUIRED = ("title", "type", "topics", "summary")
TYPES = {"paper", "engineering-blog", "docs", "abstract", "analysis", "community"}
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SUMMARY_MAX = 220


def parse_frontmatter(text: str) -> tuple[dict, bool]:
    if not text.startswith("---\n"):
        return {}, False
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, False
    meta = {}
    for line in text[4:end].splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip()] = v.strip()
    return meta, True


def strip_quotes(v: str) -> str:
    return v.strip('"').strip("'")


def entries():
    for cls in sorted(CLASSES):
        for path in sorted((REFS / cls).glob("*.md")):
            if path.name == "CATALOG.md":
                continue
            meta, ok = parse_frontmatter(path.read_text(encoding="utf-8"))
            yield cls, path, meta, ok


def lint() -> int:
    errors, warnings = [], []
    urls, titles = {}, {}
    for cls, path, meta, ok in entries():
        rel = f"{cls}/{path.name}"
        if not ok:
            errors.append(f"{rel}: 缺少合法 frontmatter（--- 块）")
            continue
        for key in REQUIRED:
            if not strip_quotes(meta.get(key, "")):
                errors.append(f"{rel}: 缺少 {key}")
        if meta.get("type") not in TYPES:
            errors.append(f"{rel}: type 非法（{meta.get('type')}），合法值 {sorted(TYPES)}")
        if meta.get("type") == "analysis" and not meta.get("url"):
            pass  # 导读类可以无 url
        elif not meta.get("url"):
            errors.append(f"{rel}: 缺少 url")
        summary = strip_quotes(meta.get("summary", ""))
        if len(summary) > SUMMARY_MAX:
            errors.append(f"{rel}: summary {len(summary)} 字超限（≤{SUMMARY_MAX}）")
        topics = meta.get("topics", "")
        if topics and not re.fullmatch(r"\[[a-z0-9 ,\-]+\]", topics):
            errors.append(f"{rel}: topics 格式应为小写 [a, b]：{topics}")
        if cls != "guides":
            stem = path.stem
            if not SLUG.fullmatch(stem) or len(stem) > 90:
                errors.append(f"{rel}: 文件名不是合法 slug")
        if not meta.get("published"):
            warnings.append(f"{rel}: 无 published")
        body_len = len(path.read_text(encoding="utf-8").split("---", 2)[-1])
        if body_len < 600:
            errors.append(f"{rel}: 正文 {body_len} 字节过短——薄内容并入 synthesis 引用，不单独建条目")
        url = meta.get("url", "")
        if url:
            if url in urls:
                errors.append(f"{rel}: url 重复（先见于 {urls[url]}）")
            else:
                urls[url] = rel
        t = strip_quotes(meta.get("title", ""))
        if t:
            if t in titles:
                errors.append(f"{rel}: title 重复（先见于 {titles[t]}）")
            else:
                titles[t] = rel
    core_cnt = Counter(cls for cls, _, meta, ok in entries() if ok and meta.get("priority") == "core")
    # synthesis 条目内的相对链接必须指向库内真实文件（防死链）
    for cls, path, meta, ok in entries():
        if not ok or cls != "synthesis":
            continue
        text = path.read_text(encoding="utf-8")
        for link in re.findall(r"\]\(([^)#\s]+\.md)\)", text):
            if not (path.parent / link).resolve().exists():
                errors.append(f"synthesis/{path.name}: 死链 {link}")
    for cls, n in core_cnt.items():
        if n > 5:
            warnings.append(f"{cls}: core 标记 {n} 篇超过 5，必读会被稀释")
    for w in warnings:
        print(f"WARN {w}")
    for e in errors:
        print(f"ERROR {e}")
    print(f"\nlint: {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


def catalog() -> int:
    total = 0
    for cls in sorted(CLASSES):
        rows = []
        for _, path, meta, ok in list(entries()):
            if path.parent.name != cls or not ok:
                continue
            published = meta.get("published", "")
            core = meta.get("priority", "") == "core"
            rows.append((core, published, path.name, meta))
        rows.sort(key=lambda r: (r[0], r[1] == "", r[1]), reverse=True)
        if not rows:
            continue
        ncore = sum(1 for r in rows if r[0])
        lines = [
            "<!-- 由 scripts/kb.py catalog 再生；手写必被覆盖。检索用 rg；单篇细节 head -8。 -->",
            f"# {cls} · {len(rows)} 篇（⭐ core 置顶，余按日期倒序）",
            "",
        ]
        for core, published, fname, meta in rows:
            topics = meta.get("topics", "").strip("[]")
            topics = ", ".join(t.strip() for t in topics.split(",")[:3])
            star = "⭐ " if core else ""
            lines.append(f"- {star}[{strip_quotes(meta['title'])}]({fname}) · {published or '日期未知'} · {topics}")
        (REFS / cls / "CATALOG.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
        total += len(rows)
        print(f"{cls}: {len(rows)} 条（core {ncore}）-> CATALOG.md")
    print(f"catalog 完成，共 {total} 条")
    return 0


def stats() -> int:
    all_entries = list(entries())
    cnt = Counter(cls for cls, *_ in all_entries)
    core = Counter(cls for cls, _, meta, ok in all_entries if ok and meta.get("priority") == "core")
    for cls, n in cnt.most_common():
        print(f"{cls:24s} {n:4d}  (core {core.get(cls, 0)})")
    print(f"{'TOTAL':24s} {sum(cnt.values()):4d}  (core {sum(core.values())})")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    sys.exit({"lint": lint, "catalog": catalog, "stats": stats}.get(cmd, lambda: (print(__doc__), 1))())
