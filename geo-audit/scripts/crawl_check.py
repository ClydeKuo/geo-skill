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

# 名单更新日期：2026-11-16（与 references/ai-crawlers.md 同步维护）
# purpose: training=模型训练采集；search=AI 搜索/检索索引；user=用户提问时实时抓取
# ua_full 为 None 表示该名称只是 robots.txt 控制标记，没有独立的抓取 UA
AI_CRAWLERS = [
    {"name": "GPTBot", "ua_token": "GPTBot", "owner": "OpenAI", "market": "global", "purpose": "training",
     "ua_full": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; GPTBot/1.3; +https://openai.com/gptbot)"},
    {"name": "OAI-SearchBot", "ua_token": "OAI-SearchBot", "owner": "OpenAI (ChatGPT 搜索)", "market": "global",
     "purpose": "search",
     "ua_full": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; OAI-SearchBot/1.3; +https://openai.com/searchbot"},
    {"name": "ChatGPT-User", "ua_token": "ChatGPT-User", "owner": "OpenAI", "market": "global", "purpose": "user",
     "ua_full": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko); compatible; ChatGPT-User/1.0; +https://openai.com/bot"},
    {"name": "ClaudeBot", "ua_token": "ClaudeBot", "owner": "Anthropic", "market": "global", "purpose": "training",
     "ua_full": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)"},
    {"name": "Claude-SearchBot", "ua_token": "Claude-SearchBot", "owner": "Anthropic", "market": "global",
     "purpose": "search",
     "ua_full": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Claude-SearchBot/1.0; +https://www.anthropic.com)"},
    {"name": "Claude-User", "ua_token": "Claude-User", "owner": "Anthropic", "market": "global", "purpose": "user",
     "ua_full": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Claude-User/1.0; +https://www.anthropic.com)"},
    {"name": "PerplexityBot", "ua_token": "PerplexityBot", "owner": "Perplexity", "market": "global",
     "purpose": "search",
     "ua_full": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; PerplexityBot/1.0; +https://perplexity.ai/perplexitybot)"},
    {"name": "Perplexity-User", "ua_token": "Perplexity-User", "owner": "Perplexity", "market": "global",
     "purpose": "user",
     "ua_full": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Perplexity-User/1.0; +https://perplexity.ai/perplexity-user)"},
    {"name": "Google-Extended", "ua_token": "Google-Extended", "owner": "Google (Gemini 训练)", "market": "global",
     "purpose": "training", "ua_full": None},
    {"name": "Googlebot", "ua_token": "Googlebot", "owner": "Google (搜索 / AI Overview)", "market": "global",
     "purpose": "search", "ua_full": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"},
    {"name": "Bingbot", "ua_token": "Bingbot", "owner": "Microsoft (Bing / Copilot，亦供 ChatGPT 部分检索)",
     "market": "global", "purpose": "search",
     "ua_full": "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)"},
    {"name": "Applebot-Extended", "ua_token": "Applebot-Extended", "owner": "Apple (Apple Intelligence 训练)",
     "market": "global", "purpose": "training", "ua_full": None},
    {"name": "Meta-ExternalAgent", "ua_token": "Meta-ExternalAgent", "owner": "Meta", "market": "global",
     "purpose": "training",
     "ua_full": "meta-externalagent/1.1 (+https://developers.facebook.com/docs/sharing/webmasters/crawler)"},
    {"name": "CCBot", "ua_token": "CCBot", "owner": "Common Crawl", "market": "global", "purpose": "training",
     "ua_full": "CCBot/2.0 (https://commoncrawl.org/faq/)"},
    {"name": "Amazonbot", "ua_token": "Amazonbot", "owner": "Amazon (Alexa / Rufus)", "market": "global",
     "purpose": "search",
     "ua_full": "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; Amazonbot/0.1; +https://developer.amazon.com/support/amazonbot) Chrome/119.0.6045.214 Safari/537.36"},
    {"name": "DuckAssistBot", "ua_token": "DuckAssistBot", "owner": "DuckDuckGo", "market": "global",
     "purpose": "search", "ua_full": "DuckAssistBot/1.2; (+http://duckduckgo.com/duckassistbot.html)"},
    {"name": "Bytespider", "ua_token": "Bytespider", "owner": "字节跳动 (豆包)", "market": "cn", "purpose": "training",
     "ua_full": "Mozilla/5.0 (Linux; Android 5.0) AppleWebKit/537.36 (KHTML, like Gecko) Mobile Safari/537.36 (compatible; Bytespider; spider-feedback@bytedance.com)"},
    {"name": "Baiduspider", "ua_token": "Baiduspider", "owner": "百度 (搜索 / 文心)", "market": "cn", "purpose": "search",
     "ua_full": "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)"},
    {"name": "Sogou web spider", "ua_token": "Sogou web spider", "owner": "搜狗 (腾讯)", "market": "cn",
     "purpose": "search",
     "ua_full": "Sogou web spider/4.0(+http://www.sogou.com/docs/help/webmasters.htm#07)"},
    {"name": "YisouSpider", "ua_token": "YisouSpider", "owner": "神马 / 夸克 (阿里)", "market": "cn", "purpose": "search",
     "ua_full": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 YisouSpider/5.0 Safari/537.36"},
    {"name": "360Spider", "ua_token": "360Spider", "owner": "360 搜索", "market": "cn", "purpose": "search",
     "ua_full": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36; 360Spider"},
    {"name": "PetalBot", "ua_token": "PetalBot", "owner": "华为 (花瓣搜索 / 小艺)", "market": "cn", "purpose": "search",
     "ua_full": "Mozilla/5.0 (compatible;PetalBot;+https://webmaster.petalsearch.com/site/petalbot)"},
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


def _xml_locs(text):
    """返回 (根标签名, [loc...])。"""
    body = re.sub(r"^\s*<\?xml[^>]*\?>", "", text or "")  # 文本已解码，去掉 encoding 声明
    try:
        root = ET.fromstring(body.strip())
    except (ET.ParseError, ValueError):
        return None, []
    locs = [el.text.strip() for el in root.iter() if el.tag.split("}")[-1] == "loc" and el.text]
    return root.tag.split("}")[-1], locs


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
    urls, used = [], []
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
        kind, locs = _xml_locs(resp["text"])
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
    return {"urls": urls, "sources": used, "count": len(urls), "truncated": state["truncated"]}


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
        value = {"status": status, "browser_status": base.get("status")}
        if status is None:
            results[c["name"]] = item("unknown", value, "请求失败（%s），未能判断" % r.get("error"))
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
        self.links = []

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        rel = a.get("rel", "").lower()
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


def run(url, proxy=None, timeout=10):
    def get(u, ua=BROWSER_UA, force_text=False):
        return fetch(u, ua=ua, proxy=proxy, timeout=timeout, force_text=force_text)

    out = {"target": url, "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    polite_sleep()
    home = get(url)
    final = home["final_url"]
    out["final_url"] = final
    hv = {k: home[k] for k in ("status", "elapsed_ms", "bytes", "content_type", "error")}
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
        value = dict(v, purpose=c["purpose"], market=c["market"], owner=c["owner"])
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
    return out


def main():
    args = base_argparser(__doc__.splitlines()[0]).parse_args()
    emit(run(normalize_url(args.url), args.proxy, args.timeout), args.out)


if __name__ == "__main__":
    safe_main(main)
