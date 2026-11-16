#!/usr/bin/env python3
"""第2/3层 单页审计：标题层级、结构、证据单元（数据/日期/引用/引语）、结构化数据、作者与更新时间。

用法：python3 page_audit.py <url> [<url> ...] [--proxy URL] [--timeout 10] [--out file.json]
"""
import json
import os
import re
import sys
import urllib.parse
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (base_argparser, count_words, emit, extract_text, fetch, item,  # noqa: E402
                     polite_sleep, registrable_domain)

_NUM_PATTERNS = [
    r"\d+(?:\.\d+)?\s*%",                                                     # 百分比
    r"[¥￥$€£]\s?\d[\d,]*(?:\.\d+)?",                                          # 货币符号
    r"\d[\d,]*(?:\.\d+)?\s*(?:元|万元|亿元|美元|USD|RMB)",                      # 货币单位
    r"\d[\d,]*(?:\.\d+)?\s*(?:万|亿|千|百万|million|billion|倍|x\b|kg|km|小时|分钟|天|人|家|次)",  # 带单位
]
_NUM = re.compile("|".join("(?:%s)" % p for p in _NUM_PATTERNS), re.I)
_DATE = re.compile(
    r"\d{4}-\d{1,2}-\d{1,2}|\d{4}/\d{1,2}/\d{1,2}|\d{4}年\d{1,2}月(?:\d{1,2}日)?|"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+(?:\d{1,2},?\s+)?\d{4}", re.I)


class _PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = None
        self._in_title = False
        self.meta = {}
        self.lang = None
        self.headings = []
        self._h = None
        self.counts = {"p": 0, "ul": 0, "ol": 0, "table": 0, "blockquote": 0}
        self.links = []
        self.jsonld = []
        self._in_jsonld = False
        self._buf = []
        self.microdata = []
        self.rel_author = None
        self._in_rel_author = False
        self.time_datetime = None

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "html" and a.get("lang"):
            self.lang = a["lang"]
        elif tag == "title" and self.title is None:
            self._in_title, self._buf = True, []
        elif tag == "meta":
            key = (a.get("name") or a.get("property") or "").lower()
            if key:
                self.meta.setdefault(key, a.get("content", ""))
        elif re.fullmatch(r"h[1-6]", tag):
            self._h, self._buf = int(tag[1]), []
        elif tag in self.counts:
            self.counts[tag] += 1
        elif tag == "script" and a.get("type", "").lower() == "application/ld+json":
            self._in_jsonld, self._buf = True, []
        elif tag == "time" and a.get("datetime") and not self.time_datetime:
            self.time_datetime = a["datetime"]
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
            if "author" in a.get("rel", "").lower().split():
                self._in_rel_author, self._buf = True, []
        if a.get("itemtype"):
            self.microdata.append(a["itemtype"].rstrip("/").rsplit("/", 1)[-1])

    def handle_endtag(self, tag):
        if tag == "title" and self._in_title:
            self.title, self._in_title = "".join(self._buf).strip(), False
        elif self._h and tag == "h%d" % self._h:
            self.headings.append({"level": self._h, "text": re.sub(r"\s+", " ", "".join(self._buf)).strip()})
            self._h = None
        elif tag == "script" and self._in_jsonld:
            self.jsonld.append("".join(self._buf))
            self._in_jsonld = False
        elif tag == "a" and self._in_rel_author:
            self.rel_author = "".join(self._buf).strip() or None
            self._in_rel_author = False

    def handle_data(self, data):
        if self._in_title or self._h or self._in_jsonld or self._in_rel_author:
            self._buf.append(data)


def _walk_jsonld(node, types, info):
    if isinstance(node, list):
        for n in node:
            _walk_jsonld(n, types, info)
    elif isinstance(node, dict):
        t = node.get("@type")
        for x in (t if isinstance(t, list) else [t]):
            if isinstance(x, str):
                types.append(x)
        author = node.get("author")
        if author and "author" not in info:
            first = author[0] if isinstance(author, list) and author else author
            name = first.get("name") if isinstance(first, dict) else first
            if isinstance(name, str):
                info["author"] = name
        if isinstance(node.get("dateModified"), str) and "date_modified" not in info:
            info["date_modified"] = node["dateModified"]
        for k, v in node.items():
            if k in ("@graph", "mainEntity", "itemListElement", "hasPart") or isinstance(v, (dict, list)):
                if k != "author":
                    _walk_jsonld(v, types, info)


def audit_html(html, url):
    p = _PageParser()
    try:
        p.feed(html or "")
        p.close()
    except Exception:
        pass
    text = extract_text(html)
    types, info = [], {}
    for block in p.jsonld:
        try:
            _walk_jsonld(json.loads(block), types, info)
        except (ValueError, TypeError):
            continue
    mine = registrable_domain(urllib.parse.urlsplit(url).hostname or "")
    external = 0
    for href in p.links:
        h = urllib.parse.urlsplit(urllib.parse.urljoin(url, href)).hostname
        if h and registrable_domain(h) != mine:
            external += 1
    skips = 0
    for prev, cur in zip(p.headings, p.headings[1:]):
        if cur["level"] > prev["level"] + 1:
            skips += 1
    return {
        "title": p.title,
        "meta_description": p.meta.get("description"),
        "lang": p.lang,
        "h1_count": sum(1 for h in p.headings if h["level"] == 1),
        "headings": p.headings,
        "heading_skips": skips,
        "paragraphs": p.counts["p"],
        "lists": p.counts["ul"] + p.counts["ol"],
        "tables": p.counts["table"],
        "word_count": count_words(text),
        "numbers": len(_NUM.findall(text)),
        "dates": len(_DATE.findall(text)),
        "external_links": external,
        "blockquotes": p.counts["blockquote"],
        "jsonld_types": list(dict.fromkeys(types)),
        "microdata_types": list(dict.fromkeys(p.microdata)),
        "author": p.meta.get("author") or info.get("author") or p.rel_author,
        "date_modified": info.get("date_modified") or p.meta.get("article:modified_time") or p.time_datetime,
        "og": {k: v for k, v in p.meta.items() if k.startswith("og:")},
    }


def audit_url(url, proxy=None, timeout=10):
    r = fetch(url, proxy=proxy, timeout=timeout)
    out = {"url": url, "final_url": r["final_url"], "status": r["status"], "result": None}
    if r["status"] != 200:
        out["check"] = item("unknown", None, "页面不可用（%s），未评估内容" % (r["error"] or r["status"]))
    elif r["content_type"] not in ("text/html", "application/xhtml+xml") or r["text"] is None:
        out["check"] = item("unknown", r["content_type"], "非 HTML 页面（%s），未评估内容" % r["content_type"])
    else:
        out["result"] = audit_html(r["text"], r["final_url"])
        detail = "已截断到 5MB 分析" if r["truncated"] else "已分析"
        out["check"] = item("pass", None, detail)
    return out


def main():
    ap = base_argparser(__doc__.splitlines()[0])
    ap.add_argument("more_urls", nargs="*")
    args = ap.parse_args()
    pages = []
    for u in [args.url] + args.more_urls:
        polite_sleep()
        pages.append(audit_url(u, args.proxy, args.timeout))
    emit({"pages": pages}, args.out)


if __name__ == "__main__":
    main()
