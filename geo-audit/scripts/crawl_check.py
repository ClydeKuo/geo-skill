#!/usr/bin/env python3
"""第1层 可抓取性检查：robots.txt 对 AI 爬虫的放行、UA 拦截对照、sitemap、首页卫生项。

用法：python3 crawl_check.py <url> [--proxy URL] [--timeout 10] [--out file.json]
"""
import datetime
import os
import re
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (BROWSER_UA, base_argparser, emit, extract_text, fetch, is_challenge,  # noqa: E402
                     item, normalize_url, polite_sleep, registrable_domain, safe_main)

MARKETS = ("cn", "us", "jp", "kr", "de", "fr", "es")
MARKET_LANG = {"cn": "zh-CN", "us": "en-US", "jp": "ja-JP", "kr": "ko-KR", "de": "de-DE", "fr": "fr-FR", "es": "es"}

# 名单更新日期：2026-11-16（与 references/ai-crawlers.md 同步维护）
# markets: ["all"] 表示全球通用，否则为相关市场代码
# purpose: training=模型训练采集；search=AI 搜索/检索索引；user=用户提问时实时抓取
# ua_full 为 None 表示该名称只是 robots.txt 控制标记，没有独立的抓取 UA
AI_CRAWLERS = [
    {"name": "GPTBot", "ua_token": "GPTBot", "owner": "OpenAI", "markets": ["all"], "purpose": "training",
     "ua_full": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.3; +https://openai.com/gptbot)"},
    {"name": "OAI-SearchBot", "ua_token": "OAI-SearchBot", "owner": "OpenAI (ChatGPT 搜索)", "markets": ["all"],
     "purpose": "search",
     "ua_full": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; OAI-SearchBot/1.3; +https://openai.com/searchbot"},
    {"name": "ChatGPT-User", "ua_token": "ChatGPT-User", "owner": "OpenAI", "markets": ["all"], "purpose": "user",
     "ua_full": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot"},
    {"name": "ClaudeBot", "ua_token": "ClaudeBot", "owner": "Anthropic", "markets": ["all"], "purpose": "training",
     "ua_full": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)"},
    {"name": "Claude-SearchBot", "ua_token": "Claude-SearchBot", "owner": "Anthropic", "markets": ["all"],
     "purpose": "search",
     "ua_full": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Claude-SearchBot/1.0; +https://www.anthropic.com)"},
    {"name": "Claude-User", "ua_token": "Claude-User", "owner": "Anthropic", "markets": ["all"], "purpose": "user",
     "ua_full": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Claude-User/1.0; +https://www.anthropic.com)"},
    {"name": "PerplexityBot", "ua_token": "PerplexityBot", "owner": "Perplexity", "markets": ["all"],
     "purpose": "search",
     "ua_full": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)"},
    {"name": "Perplexity-User", "ua_token": "Perplexity-User", "owner": "Perplexity", "markets": ["all"],
     "purpose": "user",
     "ua_full": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Perplexity-User/1.0; +https://perplexity.ai/perplexity-user)"},
    {"name": "Google-Extended", "ua_token": "Google-Extended", "owner": "Google (Gemini 训练)", "markets": ["all"],
     "purpose": "training", "ua_full": None},
    {"name": "Googlebot", "ua_token": "Googlebot", "owner": "Google (搜索 / AI Overview)", "markets": ["all"],
     "purpose": "search", "ua_full": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"},
    {"name": "Bingbot", "ua_token": "Bingbot", "owner": "Microsoft (Bing / Copilot，亦供 ChatGPT 部分检索)",
     "markets": ["all"], "purpose": "search",
     "ua_full": "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"},
    {"name": "Applebot-Extended", "ua_token": "Applebot-Extended", "owner": "Apple (Apple Intelligence 训练)",
     "markets": ["all"], "purpose": "training", "ua_full": None},
    {"name": "Meta-ExternalAgent", "ua_token": "Meta-ExternalAgent", "owner": "Meta", "markets": ["all"],
     "purpose": "training",
     "ua_full": "meta-externalagent/1.1 (+https://developers.facebook.com/docs/sharing/webmasters/crawler)"},
    {"name": "CCBot", "ua_token": "CCBot", "owner": "Common Crawl", "markets": ["all"], "purpose": "training",
     "ua_full": "CCBot/2.0 (https://commoncrawl.org/faq/)"},
    {"name": "Amazonbot", "ua_token": "Amazonbot", "owner": "Amazon (Alexa / Rufus)", "markets": ["all"],
     "purpose": "search",
     "ua_full": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Amazonbot/0.1; +https://developer.amazon.com/support/amazonbot) Chrome/119.0.6045.214 Safari/537.36"},
    {"name": "DuckAssistBot", "ua_token": "DuckAssistBot", "owner": "DuckDuckGo", "markets": ["all"],
     "purpose": "search", "ua_full": "DuckAssistBot/1.2; (+http://duckduckgo.com/duckassistbot.html)"},
    {"name": "Bytespider", "ua_token": "Bytespider", "owner": "字节跳动 (豆包)", "markets": ["cn"], "purpose": "training",
     "ua_full": "Mozilla/5.0 (Linux; Android 5.0) AppleWebKit/537.36 (KHTML, like Gecko) Mobile Safari/537.36 (compatible; Bytespider; spider-feedback@bytedance.com)"},
    {"name": "Baiduspider", "ua_token": "Baiduspider", "owner": "百度 (搜索 / 文心)", "markets": ["cn"], "purpose": "search",
     "ua_full": "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)"},
    {"name": "Sogou web spider", "ua_token": "Sogou web spider", "owner": "搜狗 (腾讯)", "markets": ["cn"],
     "purpose": "search",
     "ua_full": "Sogou web spider/4.0(+http://www.sogou.com/docs/help/webmasters.htm#07)"},
    {"name": "YisouSpider", "ua_token": "YisouSpider", "owner": "神马 / 夸克 (阿里)", "markets": ["cn"], "purpose": "search",
     "ua_full": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 YisouSpider/5.0 Safari/537.36"},
    {"name": "360Spider", "ua_token": "360Spider", "owner": "360 搜索", "markets": ["cn"], "purpose": "search",
     "ua_full": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36; 360Spider"},
    {"name": "PetalBot", "ua_token": "PetalBot", "owner": "华为 (花瓣搜索 / 小艺)", "markets": ["cn"], "purpose": "search",
     "ua_full": "Mozilla/5.0 (compatible;PetalBot;+https://webmaster.petalsearch.com/site/petalbot)"},
    {"name": "MistralAI-User", "ua_token": "MistralAI-User", "owner": "Mistral (Le Chat / Vibe)", "markets": ["all"],
     "purpose": "user",
     "ua_full": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; MistralAI-User/1.0; +https://docs.mistral.ai/robots)"},
    {"name": "MistralAI-Index", "ua_token": "MistralAI-Index", "owner": "Mistral (Le Chat / Vibe 搜索索引)",
     "markets": ["all"], "purpose": "search",
     "ua_full": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; MistralAI-Index/1.0; +https://docs.mistral.ai/robots)"},
    {"name": "MistralAI-Training", "ua_token": "MistralAI-Training", "owner": "Mistral", "markets": ["all"],
     "purpose": "training",
     "ua_full": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; MistralAI-Training/1.0; +https://docs.mistral.ai/robots)"},
    {"name": "Yeti", "ua_token": "Yeti", "owner": "Naver (搜索 / AI Briefing)", "markets": ["kr"], "purpose": "search",
     "ua_full": "Mozilla/5.0 (compatible; Yeti/1.1; +https://naver.me/spd)"},
    {"name": "Daum", "ua_token": "Daum", "owner": "Daum (原 Kakao 运营的搜索)", "markets": ["kr"], "purpose": "search",
     "ua_full": "Mozilla/5.0 (compatible; Daum/4.1; +http://cs.daum.net/faq/15/4118.html?faqId=28966)"},
]

_ICP = re.compile(r"[\u4e00-\u9fa5]ICP[备证]\d+号(?:-\d+)?")


def _origin(url):
    p = urllib.parse.urlsplit(url)
    return "%s://%s" % (p.scheme, p.netloc)


def _is_html(text):
    t = (text or "").lstrip().lower()
    return t.startswith("<") or "<html" in t


def _parse_robots(robots_text):
    """按 RFC 9309 解析为 [(agents:set, rules:[(allow:bool, pattern:str)])]。"""
    groups, agents, rules, last_was_agent = [], set(), [], False
    for raw in (robots_text or "").lstrip("\ufeff").splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key, value = key.strip().lower(), value.strip()
        if key == "user-agent":
            if not last_was_agent and (agents or rules):
                groups.append((agents, rules))
                agents, rules = set(), []
            agents.add(value.split("/")[0].strip().lower())
            last_was_agent = True
        elif key in ("allow", "disallow"):
            last_was_agent = False
            if agents and value:  # 空 Disallow 表示不限制
                rules.append((key == "allow", value))
        else:
            last_was_agent = False if key != "sitemap" else last_was_agent
    if agents:
        groups.append((agents, rules))
    return groups


def _pattern_matches(pattern, path):
    anchored = pattern.endswith("$")
    body = pattern[:-1] if anchored else pattern
    regex = ".*".join(re.escape(part) for part in body.split("*"))
    return re.match(regex + ("$" if anchored else ""), path) is not None


def _rules_allow(rules, path):
    """最长匹配规则生效；长度相同时 Allow 优先；没有匹配则允许。"""
    best = None  # (length, allow)
    for allow, pattern in rules:
        if _pattern_matches(pattern, path):
            cand = (len(pattern), allow)
            if best is None or cand[0] > best[0] or (cand[0] == best[0] and allow):
                best = cand
    return True if best is None else best[1]


_UNREACHABLE = "robots.txt 无法读取（%s），无法判断各爬虫是否被放行"


def robots_verdicts(robots_status, robots_text, site_url, challenged=False):
    """判断每个 AI 爬虫能否抓取站点首页路径 /（RFC 9309 语义）。

    source: ok | missing（4xx，视为全部放行）| soft404（返回 HTML，视为全部放行）
            | unreachable（网络错误 / 429 / 5xx / 挑战页，allowed 为 None）
    """
    bots = {}
    if challenged:
        source, detail = "unreachable", _UNREACHABLE % "审计机被 WAF/CDN 挑战页拦截"
    elif robots_status is None:
        source, detail = "unreachable", _UNREACHABLE % "网络错误"
    elif robots_status == 429 or robots_status >= 500:
        source, detail = "unreachable", _UNREACHABLE % ("HTTP %s；按 RFC 9309，5xx 时爬虫会视为全站禁止" % robots_status)
    elif robots_status >= 400:
        source, detail = "missing", "robots.txt 返回 %s，按规范视为全部放行" % robots_status
    elif robots_text is None or _is_html(robots_text):
        source, detail = "soft404", "robots.txt 返回的是 HTML 页面（软 404），视为全部放行"
    else:
        source, detail = "ok", "robots.txt 正常解析"
    if source != "ok":
        allowed = None if source == "unreachable" else True
        for c in AI_CRAWLERS:
            bots[c["name"]] = {"allowed": allowed, "matched_group": "none"}
        return {"source": source, "detail": detail, "bots": bots}

    groups = _parse_robots(robots_text)
    path = urllib.parse.urlsplit(urllib.parse.urljoin(site_url, "/")).path or "/"
    for c in AI_CRAWLERS:
        token = c["ua_token"].lower()
        specific = [rules for agents, rules in groups if token in agents]
        if specific:
            group, rules = "specific", [r for rs in specific for r in rs]
        else:
            wild = [rules for agents, rules in groups if "*" in agents]
            group, rules = ("wildcard", [r for rs in wild for r in rs]) if wild else ("none", [])
        bots[c["name"]] = {"allowed": _rules_allow(rules, path), "matched_group": group}
    return {"source": source, "detail": detail, "bots": bots}


def _xml_parse(text):
    """返回 (根标签名, [loc...], [alternate...])；alternate 为 {"loc","lang","href"}。"""
    body = re.sub(r"^\s*<\?xml[^>]*\?>", "", text or "")  # 文本已解码，去掉 encoding 声明
    try:
        root = ET.fromstring(body.strip())
    except (ET.ParseError, ValueError):
        return None, [], []
    kind = root.tag.split("}")[-1]
    locs, alts = [], []
    for el in root:
        loc = None
        for child in el:
            name = child.tag.split("}")[-1]
            if name == "loc" and child.text:
                loc = child.text.strip()
                locs.append(loc)
            elif name == "link" and child.get("rel") == "alternate" and child.get("hreflang") and loc:
                alts.append({"loc": loc, "lang": child.get("hreflang").lower(), "href": child.get("href")})
    return kind, locs, alts


def _xml_locs(text):
    kind, locs, _ = _xml_parse(text)
    return kind, locs


def parse_sitemaps(robots_text, fetcher, origin=None, limit=500, max_files=30, max_depth=3):
    """读取 robots.txt 声明的 sitemap（无声明则试 /sitemap.xml），sitemapindex 最多递归 max_depth 层。

    count 为实际读取到的 URL 数（不超过 limit）；truncated=True 表示因上限没有读完。
    """
    sources = []
    for line in (robots_text or "").splitlines():
        if line.strip().lower().startswith("sitemap:"):
            value = line.split(":", 1)[1].strip()
            sources.append(urllib.parse.urljoin(origin + "/", value) if origin else value)
    if not sources and origin:
        sources = [origin + "/sitemap.xml"]
    urls, used, alternates = [], [], []
    state = {"truncated": False, "files": 0}

    def walk(u, depth):
        if len(urls) >= limit or state["files"] >= max_files:
            state["truncated"] = True
            return
        state["files"] += 1
        polite_sleep()
        resp = fetcher(u)
        if resp.get("status") != 200 or resp.get("text") is None:
            return
        used.append(u)
        kind, locs, alts = _xml_parse(resp["text"])
        alternates.extend(alts[:max(0, 200 - len(alternates))])
        if kind == "sitemapindex":
            if depth >= max_depth:
                state["truncated"] = True
                return
            for child in locs:
                walk(urllib.parse.urljoin(u, child), depth + 1)
        else:
            for loc in locs:
                if loc not in urls:
                    if len(urls) >= limit:
                        state["truncated"] = True
                        return
                    urls.append(loc)

    for src in sources:
        walk(src, 1)
    return {"urls": urls, "sources": used, "count": len(urls), "truncated": state["truncated"],
            "alternates": alternates}


def ua_block_check(url, fetcher_by_ua):
    """以浏览器 UA 做对照，逐个用检索/用户触发类 AI 爬虫 UA 请求首页。"""
    polite_sleep()
    base = fetcher_by_ua(BROWSER_UA)
    base_ok = base.get("status") == 200 and not is_challenge(base)
    results = {}
    for c in AI_CRAWLERS:
        if c["purpose"] == "training" or not c["ua_full"]:
            continue
        polite_sleep()
        r = fetcher_by_ua(c["ua_full"])
        status = r.get("status")
        value = {"status": status, "browser_status": base.get("status"), "rate_limited": bool(r.get("rate_limited"))}
        if status is None:
            results[c["name"]] = item("unknown", value, "请求失败（%s），未能判断" % r.get("error"))
            continue
        if status == 429:
            results[c["name"]] = item("unknown", value, "被限流，未能判断")
            continue
        blocked = status in (401, 403, 429, 503) or is_challenge(r)
        if not blocked:
            results[c["name"]] = item("pass", value, "AI UA 访问正常")
        elif base_ok:
            results[c["name"]] = item(
                "suspect", value,
                "浏览器 UA 正常而该 AI UA 被拦（%s）。脚本是伪装 UA，CDN 可能按 IP 识别真实爬虫，"
                "请核对 CDN/WAF 的 AI bot 设置或服务器日志" % status)
        else:
            results[c["name"]] = item("warn", value, "浏览器 UA 也被拦截（%s），站点拦截所有自动化请求" % base.get("status"))
    return results


class _HeadParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.canonical = None
        self.meta_robots = []
        self.hreflang = []
        self.hreflang_map = {}
        self.html_lang = None
        self.links = []

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        rel = a.get("rel", "").lower()
        if tag == "html" and a.get("lang"):
            self.html_lang = a["lang"]
        if tag == "link" and "alternate" in rel.split() and a.get("hreflang") and a.get("href"):
            self.hreflang_map.setdefault(a["hreflang"].lower(), a["href"])
        if tag == "link" and "canonical" in rel.split():
            self.canonical = a.get("href")
        elif tag == "link" and "alternate" in rel.split() and a.get("hreflang"):
            self.hreflang.append(a.get("href"))
        elif tag == "meta" and a.get("name", "").lower() in ("robots", "googlebot", "bingbot", "baiduspider"):
            self.meta_robots.append("%s: %s" % (a.get("name"), a.get("content", "")))
        elif tag == "a" and a.get("href"):
            self.links.append(a["href"])


def _other_domains(final_url, parser):
    host = urllib.parse.urlsplit(final_url).hostname or ""
    mine = registrable_domain(host)
    label = mine.split(".")[0]
    found = set()
    for href in parser.hreflang + parser.links:
        h = urllib.parse.urlsplit(urllib.parse.urljoin(final_url, href)).hostname
        if not h:
            continue
        rd = registrable_domain(h)
        if rd != mine and rd.split(".")[0] == label:
            found.add(rd)
    return sorted(found)


_LINK_ITEM = re.compile(r"<([^>]+)>\s*;([^,]*(?:\"[^\"]*\"[^,]*)*)")


def parse_link_header(value):
    """HTTP Link 头中的 rel=alternate; hreflang=xx → {lang小写: url}。"""
    out = {}
    for m in _LINK_ITEM.finditer(value or ""):
        url, params = m.group(1).strip(), m.group(2)
        rel = re.search(r'rel\s*=\s*"?([^";]+)"?', params, re.I)
        lang = re.search(r'hreflang\s*=\s*"?([^";]+)"?', params, re.I)
        if rel and "alternate" in rel.group(1).lower().split() and lang:
            out.setdefault(lang.group(1).strip().lower(), url)
    return out


def norm_url(url):
    """比较用的 URL 归一化：scheme/host 小写、去 fragment、去路径末尾斜杠（根路径为 /）。格式错误时原样小写返回。"""
    try:
        p = urllib.parse.urlsplit((url or "").strip())
    except ValueError:
        return (url or "").strip().lower()
    path = p.path.rstrip("/") or "/"
    if path == "/" and not p.query:
        path = ""
    return urllib.parse.urlunsplit((p.scheme.lower(), p.netloc.lower(), path, p.query, ""))


MAX_ALTERNATES = 10


def _market_rank(lang, markets):
    """目标市场对应的语言排前面：完全匹配 0、主语言匹配 1、其他 2。"""
    best = 2
    for m in markets or []:
        tag = MARKET_LANG.get(m, "").lower()
        if not tag:
            continue
        if lang == tag:
            return 0
        if lang.split("-")[0] == tag.split("-")[0]:
            best = 1
    return best


def _alt_value(url, r):
    return {"url": url, "status": r.get("status"), "rate_limited": bool(r.get("rate_limited"))}


def hreflang_check(final_url, html_alts, header_alts, sitemap_alts, html_lang, fetcher, markets=None):
    """合并三种来源的 hreflang 声明，并检查每个备用版本可访问、不跳转且回链到首页。"""
    declared, x_default, malformed = {}, None, {}
    for source, alts in (("html", html_alts), ("header", header_alts), ("sitemap", sitemap_alts)):
        for lang, href in (alts or {}).items():
            lang = (lang or "").strip().lower()
            if not lang or not href:
                continue
            try:
                href = urllib.parse.urljoin(final_url, href)
                urllib.parse.urlsplit(href)
            except ValueError:
                malformed.setdefault(lang, href)
                continue
            if lang == "x-default":
                x_default = x_default or href
                continue
            entry = declared.setdefault(lang, {"url": href, "sources": []})
            if source not in entry["sources"]:
                entry["sources"].append(source)
    out = {"declared": declared, "x_default": x_default, "html_lang": html_lang, "alternates": {}}
    for lang, href in malformed.items():
        out["alternates"][lang] = item("fail", {"url": href, "status": None, "rate_limited": False},
                                       "hreflang 中的 URL 格式错误")
    if not declared and not malformed:
        out["check"] = item("warn", None, "未声明 hreflang（HTML、HTTP Link 头、sitemap 均无）")
        return out
    home = norm_url(final_url)
    order = sorted(declared, key=lambda lg: _market_rank(lg, markets))
    for lang in order[:MAX_ALTERNATES]:
        entry = declared[lang]
        if norm_url(entry["url"]) == home:
            out["alternates"][lang] = item("pass", {"url": entry["url"], "status": None, "rate_limited": False},
                                           "即首页本身")
            continue
        polite_sleep()
        r = fetcher(entry["url"])
        value = _alt_value(entry["url"], r)
        if r.get("status") is None or r.get("status") == 429 or is_challenge(r):
            out["alternates"][lang] = item("unknown", value, "未能检测（%s）" % (
                "被限流" if r.get("status") == 429 else "被挑战页拦截" if is_challenge(r) else r.get("error")))
            continue
        if r.get("status") != 200:
            out["alternates"][lang] = item("fail", value, "备用版本不可访问（%s）" % r.get("status"))
            continue
        landed = r.get("final_url") or entry["url"]
        if norm_url(landed) != norm_url(entry["url"]):
            out["alternates"][lang] = item("fail", value, "备用版本跳转到 %s" % landed)
            continue
        p = _HeadParser()
        try:
            p.feed(r.get("text") or "")
        except Exception:
            pass
        backs = list(p.hreflang_map.values()) + list(
            parse_link_header((r.get("headers") or {}).get("link")).values())
        back_norm = set()
        for b in backs:
            try:
                back_norm.add(norm_url(urllib.parse.urljoin(landed, b)))
            except ValueError:
                continue
        if home in back_norm:
            out["alternates"][lang] = item("pass", value, "可访问且回链首页")
        else:
            out["alternates"][lang] = item("warn", value, "未回链首页（hreflang 不双向）")
    if len(order) > MAX_ALTERNATES:
        out["skipped"] = order[MAX_ALTERNATES:]
    statuses = [v["status"] for v in out["alternates"].values() if v["status"] != "unknown"]
    worst = "fail" if "fail" in statuses else "warn" if "warn" in statuses else "pass" if statuses else "unknown"
    out["check"] = item(worst, len(declared), "声明了 %d 个语言版本" % len(declared))
    return out


def run(url, proxy=None, timeout=10, markets=None, lang=None):
    def get(u, ua=BROWSER_UA, force_text=False):
        return fetch(u, ua=ua, proxy=proxy, timeout=timeout, force_text=force_text, lang=lang)

    markets = list(markets) if markets else list(MARKETS)
    out = {"target": url, "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "markets": markets}
    polite_sleep()
    home = get(url)
    final = home["final_url"]
    out["final_url"] = final
    hv = {k: home.get(k) for k in ("status", "elapsed_ms", "bytes", "content_type", "error", "rate_limited")}
    home_challenged = is_challenge(home)
    if home_challenged:
        out["homepage"] = item("unknown", hv, "审计机被 WAF/CDN 挑战页拦截（%s），不代表网站不可用，"
                                              "需从其他网络或由客户核实" % home["status"])
    elif home["status"] == 200:
        out["homepage"] = item("pass", hv, "首页 200，%d ms" % home["elapsed_ms"])
    else:
        out["homepage"] = item("fail", hv, "首页不可用：%s" % (home["error"] or home["status"]))

    origin = _origin(final)
    polite_sleep()
    rob = get(origin + "/robots.txt", force_text=True)
    verdicts = robots_verdicts(rob["status"], rob["text"], final, challenged=is_challenge(rob))
    robots_status = {"ok": "pass", "unreachable": "unknown"}.get(verdicts["source"], "warn")
    out["robots"] = item(robots_status,
                         {"url": origin + "/robots.txt", "status": rob["status"], "source": verdicts["source"]},
                         verdicts["detail"])
    crawlers = {}
    for c in AI_CRAWLERS:
        v = verdicts["bots"][c["name"]]
        relevant = "all" in c["markets"] or bool(set(c["markets"]) & set(markets))
        value = dict(v, purpose=c["purpose"], markets=c["markets"], owner=c["owner"], relevant=relevant)
        if v["allowed"] is None:
            crawlers[c["name"]] = item("unknown", value, "robots.txt 无法读取，未能判断")
        elif v["allowed"]:
            crawlers[c["name"]] = item("pass", value, "放行")
        elif c["purpose"] == "training":
            crawlers[c["name"]] = item("warn", value, "拦截训练爬虫：可接受，不影响 AI 搜索实时引用，但影响模型对品牌的先验认知")
        else:
            crawlers[c["name"]] = item("fail", value, "拦截检索/用户触发爬虫：该 AI 搜索无法抓取本站（P0）")
    out["ai_crawlers"] = crawlers

    if home["status"] == 200 or home_challenged:
        out["ua_blocking"] = ua_block_check(final, lambda ua: get(final, ua=ua))
    else:
        out["ua_blocking"] = {}

    sm = parse_sitemaps(rob["text"] if verdicts["source"] == "ok" else None, get, origin=origin)
    if not sm["count"]:
        sm_detail = "未找到可用 sitemap"
    elif sm["truncated"]:
        sm_detail = "已读取 %d 个 URL（达到读取上限，sitemap 未读完，不代表全站总数）" % sm["count"]
    else:
        sm_detail = "sitemap 共 %d 个 URL（已全部读取）" % sm["count"]
    out["sitemap"] = item("pass" if sm["count"] else "warn", sm, sm_detail)

    parser = _HeadParser()
    try:
        parser.feed(home["text"] or "")
    except Exception:
        pass
    if parser.canonical:
        canon = urllib.parse.urljoin(final, parser.canonical)
        same = canon.rstrip("/") == final.rstrip("/")
        out["canonical"] = item("pass" if same else "warn", canon,
                                "canonical 指向自身" if same else "canonical 指向其他 URL，请确认是否有意")
    else:
        out["canonical"] = item("warn", None, "首页未声明 canonical")
    def _directives(meta):
        return [d.strip().lower() for d in meta.split(": ", 1)[-1].split(",")]
    noindex = [m for m in parser.meta_robots if {"noindex", "none"} & set(_directives(m))]
    out["meta_robots"] = item("fail" if noindex else "pass", parser.meta_robots,
                              "meta robots 含 noindex" if noindex else "无 noindex")
    xrt = home["headers"].get("x-robots-tag")
    out["x_robots_tag"] = item("fail" if xrt and "noindex" in xrt.lower() else "pass", xrt,
                               "X-Robots-Tag 含 noindex" if xrt and "noindex" in xrt.lower() else "无阻断")
    https = final.startswith("https://")
    out["https"] = item("pass" if https else "warn", https, "最终地址为 HTTPS" if https else "最终地址不是 HTTPS")

    polite_sleep()
    llms = get(origin + "/llms.txt")
    has_llms = llms["status"] == 200 and llms["text"] is not None and not _is_html(llms["text"])
    out["llms_txt"] = item("pass", has_llms, "%s。仅记录：llms.txt 对 AI 引用无可测效果（E10），无需处理" % (
        "存在" if has_llms else "不存在"))

    m = _ICP.search(extract_text(home["text"] or "") + (home["text"] or ""))
    out["icp"] = item("pass", m.group(0), "首页展示 ICP 备案号") if m else item(
        "warn", None, "首页未找到 ICP 备案号（仅国内市场相关）")
    others = _other_domains(final, parser)
    out["other_domains"] = item("pass", others, "发现疑似同品牌其他域名，可另行审计" if others else "未发现")
    home_norm = norm_url(final)
    sitemap_alts = {a["lang"]: a["href"] for a in sm.get("alternates", [])
                    if a.get("href") and norm_url(a["loc"]) == home_norm}
    out["hreflang"] = hreflang_check(final, parser.hreflang_map, parse_link_header(home["headers"].get("link")),
                                     sitemap_alts, parser.html_lang, get, markets=markets)
    return out


def main():
    ap = base_argparser(__doc__.splitlines()[0])
    ap.add_argument("--markets", default=None, help="目标市场代码，逗号分隔：%s" % ",".join(MARKETS))
    ap.add_argument("--lang", default=None, help="请求语言（BCP 47），如 ja-JP")
    args = ap.parse_args()
    markets = None
    if args.markets:
        markets = [m.strip().lower() for m in args.markets.split(",") if m.strip()]
        unknown = [m for m in markets if m not in MARKETS]
        if unknown:
            ap.error("未知市场代码：%s（可选：%s）" % (",".join(unknown), ",".join(MARKETS)))
    emit(run(normalize_url(args.url), args.proxy, args.timeout, markets=markets, lang=args.lang), args.out)


if __name__ == "__main__":
    safe_main(main)
