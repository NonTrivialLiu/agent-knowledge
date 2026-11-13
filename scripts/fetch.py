#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests>=2.32,<3",
#   "beautifulsoup4>=4.13,<5",
#   "markdownify>=1.2,<2",
#   "trafilatura>=1.12",
#   "pymupdf4llm>=0.0.20",
# ]
# ///
"""抓取网页/论文为 Markdown，供 agent-knowledge 入库。

用法：
  uv run scripts/fetch.py URL [--title "标题"] [--published 2026-01-02] [--out 路径.md]

默认把正文 Markdown 打到 stdout，并在最前面给出建议的 frontmatter 模板；
--out 时写入文件。已处理的常见源：arXiv(abs->html)、developers.openai.com(.md)、
PDF(转 Markdown)。正文清洗沿袭旧 refresh_sources.py（标题唯一 H1、层级≤3、
相对链接绝对化、站点杂质截断）。失败时换 WebFetch / MinerU 再人工清洗。
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag
from markdownify import markdownify
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; agent-knowledge/1.0)"}


def session() -> requests.Session:
    client = requests.Session()
    client.headers.update(HEADERS)
    retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    client.mount("https://", HTTPAdapter(max_retries=retry))
    return client


def get(client: requests.Session, url: str) -> requests.Response:
    r = client.get(url, timeout=60)
    r.raise_for_status()
    if "text/" in r.headers.get("content-type", ""):
        r.encoding = "utf-8"
    return r


def clean_markdown(text: str, url: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(?m)^\s*>?\s*For the complete documentation index[^\n]*\n?", "", text)

    def absolute_link(m: re.Match[str]) -> str:
        return m.group(1) + urljoin(url, m.group(2)) + m.group(3)

    text = re.sub(r"(\]\()((?:/|\./|\.\./)[^\s)]+)(\))", absolute_link, text)
    text = re.sub(r"\[([^\]]+)\]\(mailto:\)", r"\1", text)
    text = re.sub(r"!\[\]\(\)", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    lines, seen_title, fence, last = [], False, False, 0
    for line in text.strip().splitlines():
        if re.match(r"^\s*(`{3,}|~{3,})", line):
            fence = not fence
        heading = re.match(r"^(#{1,6})\s+(.+)$", line) if not fence else None
        if heading:
            level = len(heading.group(1))
            if not seen_title:
                seen_title, level = True, 1
            elif level == 1:
                level = 2
            if last and level > last + 1:
                level = last + 1
            level = min(level, 3)
            label = re.sub(r"^(?:#{1,6}\s+)+", "", heading.group(2)).strip()
            line, last = "#" * level + " " + label, level
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def article_body(html: str, url: str, expected_title: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    host = requests.utils.urlparse(url).hostname or ""
    selectors = ["article", "main", "[role=main]"]
    if "langchain.com" in host:
        selectors.insert(0, ".blog-post-content")
    elif "metr.org" in host:
        selectors.insert(0, ".post-content")
    candidates = [n for s in selectors for n in soup.select(s)]
    if not candidates:
        raise ValueError(f"找不到正文节点，改用 trafilatura 或 WebFetch")
    body = candidates[0] if host in ("langchain.com", "metr.org") else max(
        candidates, key=lambda n: len(n.get_text(" ", strip=True)))
    if not isinstance(body, Tag):
        raise ValueError("正文节点无效")
    title_node = body.find("h1") or soup.find("h1")
    title = title_node.get_text(" ", strip=True) if title_node else expected_title
    for n in body.select("script, style, nav, footer, aside, form, button, noscript, iframe"):
        n.decompose()
    for n in body.select("[class*=share], [class*=newsletter], [class*=related-post]"):
        n.decompose()
    for n in body.select("math"):
        latex = n.get("alttext")
        if not latex:
            ann = n.select_one('annotation[encoding="application/x-tex"]')
            latex = ann.get_text(" ", strip=True) if ann else None
        if latex:
            fence = "$$" if n.get("display") == "block" else "$"
            n.replace_with(f"{fence}{latex}{fence}")
    for n in body.select("a[href], img[src]"):
        key = "href" if n.name == "a" else "src"
        n[key] = urljoin(url, n[key])
    if title_node and title_node in body.descendants:
        title_node.decompose()
    text = markdownify(str(body), heading_style="ATX", bullets="-",
                       escape_asterisks=False, escape_underscores=False)
    cutoffs = {
        "anthropic.com": [r"^## Get the developer newsletter\s*$", r"^### Want to learn more\?\s*$"],
        "cursor.com": [r"^## Related posts\s*$"],
        "arize.com": [r"^## Get the latest on AI & Observability\s*$"],
        "cloudflare.com": [r"^## Related tags\s*$"],
    }
    for domain, patterns in cutoffs.items():
        if domain in host:
            for pattern in patterns:
                marker = re.search(pattern, text, re.M)
                if marker:
                    text = text[: marker.start()]
    return title, clean_markdown(f"# {title}\n\n{text}", url)


def fetch(url: str, expected_title: str) -> tuple[str, str]:
    """返回 (title, markdown正文)。"""
    if "arxiv.org/abs/" in url:
        url = url.replace("/abs/", "/html/")
    if "developers.openai.com" in url:
        url = url.rstrip("/") + ".md"
    client = session()
    r = get(client, url)
    if r.content.startswith(b"%PDF") or "pdf" in r.headers.get("content-type", ""):
        import pymupdf, pymupdf4llm
        with pymupdf.open(stream=r.content, filetype="pdf") as doc:
            body = pymupdf4llm.to_markdown(doc, show_progress=False)
        title = expected_title or (doc.metadata.get("title") or "")
        return title, clean_markdown(f"# {title}\n\n{body}", url)
    if r.text.lstrip().startswith(("# ", "---\n")) and "<!DOCTYPE" not in r.text[:200].upper():
        text = clean_markdown(r.text, url)
        m = re.match(r"(?m)^# (.+)$", text)
        return (m.group(1) if m else expected_title), text
    soup_html = r.text
    try:
        title, body = article_body(soup_html, str(r.url), expected_title)
    except ValueError:
        import trafilatura
        body_md = trafilatura.extract(
            soup_html, output_format="markdown", include_links=True,
            include_tables=True, include_formatting=True) or ""
        title = expected_title
        body = clean_markdown(f"# {title}\n\n{body_md}", url)
    if title.lower().startswith("arxiv:"):
        body = re.sub(r"\A# [^\n]+", f"# {expected_title}", body, count=1)
        title = expected_title
    return title, body


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("url")
    ap.add_argument("--title", default="", help="页面标题（抓取自动识别失败时使用）")
    ap.add_argument("--published", default="", help="发布日期 YYYY-MM-DD")
    ap.add_argument("--out", type=Path, default=None, help="写出路径；缺省打印到 stdout")
    args = ap.parse_args()
    title, body = fetch(args.url, args.title)
    if len(body) < 1200:
        print(f"警告：正文仅 {len(body)} 字符，可能是付费墙/JS 渲染页，改用 WebFetch 或内置浏览器。", file=sys.stderr)
    fm = (
        "---\n"
        f'title: "{title.replace(chr(34), chr(39))}"\n'
        f"url: {args.url}\n"
        f"published: {args.published}\n"
        f"fetched: {date.today().isoformat()}\n"
        "type: engineering-blog  # paper / engineering-blog / docs / abstract / analysis\n"
        "topics: [分类名, 来源方, 2-3个关键词]\n"
        'summary: "一行中文摘要，≤120字，写清这条内容的独特增量"\n'
        "---\n"
    )
    out_text = fm + "\n" + body
    if args.out:
        if args.out.exists():
            raise SystemExit(f"已存在：{args.out}（入库前先去重）")
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(out_text, encoding="utf-8")
        print(f"已写入 {args.out}（记得补全 frontmatter 再 lint）", file=sys.stderr)
    else:
        sys.stdout.write(out_text)


if __name__ == "__main__":
    main()
