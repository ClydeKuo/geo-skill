#!/usr/bin/env python3
"""第1层 可抓取性检查：robots.txt 对 AI 爬虫的放行、UA 拦截对照、sitemap、首页卫生项。

用法：python3 crawl_check.py <url> [--proxy URL] [--timeout 10] [--out file.json]
"""
import datetime
import os
import re
import sys
import urllib.parse
import urllib.robotparser
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (BROWSER_UA, base_argparser, emit, extract_text, fetch, item,  # noqa: E402
                     polite_sleep, registrable_domain)

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

_CHALLENGE = re.compile(r"cf-chl|challenge-platform|captcha|just a moment", re.I)
_ICP = re.compile(r"[\u4e00-\u9fa5]ICP[备证]\d+号(?:-\d+)?")


def _origin(url):
    p = urllib.parse.urlsplit(url)
    return "%s://%s" % (p.scheme, p.netloc)


def _is_html(text):
    t = (text or "").lstrip().lower()
    return t.startswith("<") or "<html" in t


def _ua_groups(robots_text):
    """返回 robots.txt 中出现的 User-agent 值（小写）。"""
    agents = []
    for line in (robots_text or "").splitlines():
        line = line.split("#", 1)[0].strip()
        if line.lower().startswith("user-agent:"):
            agents.append(line.split(":", 1)[1].strip().lower())
    return agents


def robots_verdicts(robots_status, robots_text, site_url):
    """判断每个 AI 爬虫能否抓取站点首页路径 /。"""
    bots = {}
    if robots_status is None:
        source, detail = "error", "robots.txt 无法获取（网络错误），按全部放行处理"
    elif robots_status >= 400:
        source, detail = "missing", "robots.txt 返回 %s，按规范视为全部放行" % robots_status
    elif _is_html(robots_text):
        source, detail = "soft404", "robots.txt 返回的是 HTML 页面（软 404），视为全部放行"
    else:
        source, detail = "ok", "robots.txt 正常解析"
    if source != "ok":
        for c in AI_CRAWLERS:
            bots[c["name"]] = {"allowed": True, "matched_group": "none"}
        return {"source": source, "detail": detail, "bots": bots}

    rp = urllib.robotparser.RobotFileParser()
    rp.parse(robots_text.splitlines())
    rp.modified()
    agents = _ua_groups(robots_text)
    target = urllib.parse.urljoin(site_url, "/")
    for c in AI_CRAWLERS:
        token = c["ua_token"].lower()
        if any(a != "*" and a and a in token for a in agents):
            group = "specific"
        elif "*" in agents:
            group = "wildcard"
        else:
            group = "none"
        bots[c["name"]] = {"allowed": rp.can_fetch(c["ua_token"], target), "matched_group": group}
    return {"source": source, "detail": detail, "bots": bots}


def _xml_locs(text):
    """返回 (根标签名, [loc...])。"""
    try:
        root = ET.fromstring(text.strip().encode("utf-8"))
    except ET.ParseError:
        return None, []
    locs = [el.text.strip() for el in root.iter() if el.tag.split("}")[-1] == "loc" and el.text]
    return root.tag.split("}")[-1], locs


def parse_sitemaps(robots_text, fetcher, origin=None, limit=500):
    """读取 robots.txt 声明的 sitemap（无声明则试 /sitemap.xml），sitemapindex 递归一层。"""
    sources = []
    for line in (robots_text or "").splitlines():
        if line.strip().lower().startswith("sitemap:"):
            sources.append(line.split(":", 1)[1].strip())
    if not sources and origin:
        sources = [origin + "/sitemap.xml"]
    urls, used = [], []

    def load(u):
        polite_sleep()
        resp = fetcher(u)
        if resp.get("status") != 200 or resp.get("text") is None:
            return None, []
        used.append(u)
        return _xml_locs(resp["text"])

    for src in sources[:10]:
        kind, locs = load(src)
        if kind == "sitemapindex":
            for child in locs[:20]:
                urls += load(child)[1]
                if len(urls) >= limit:
                    break
        else:
            urls += locs
        if len(urls) >= limit:
            break
    urls = list(dict.fromkeys(urls))
    return {"urls": urls[:limit], "sources": used, "count": len(urls)}


def ua_block_check(url, fetcher_by_ua):
    """以浏览器 UA 做对照，逐个用检索/用户触发类 AI 爬虫 UA 请求首页。"""
    polite_sleep()
    base = fetcher_by_ua(BROWSER_UA)
    base_ok = base.get("status") == 200 and not _CHALLENGE.search(base.get("text") or "")
    results = {}
    for c in AI_CRAWLERS:
        if c["purpose"] == "training" or not c["ua_full"]:
            continue
        polite_sleep()
        r = fetcher_by_ua(c["ua_full"])
        status = r.get("status")
        blocked = (status in (401, 403, 429, 503) or status is None
                   or bool(_CHALLENGE.search(r.get("text") or "")))
        value = {"status": status, "browser_status": base.get("status")}
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
    def get(u, ua=BROWSER_UA):
        return fetch(u, ua=ua, proxy=proxy, timeout=timeout)

    out = {"target": url, "fetched_at": datetime.datetime.now(datetime.timezone.utc).isoformat()}
    polite_sleep()
    home = get(url)
    final = home["final_url"]
    out["final_url"] = final
    hv = {k: home[k] for k in ("status", "elapsed_ms", "bytes", "content_type", "error")}
    if home["status"] == 200:
        out["homepage"] = item("pass", hv, "首页 200，%d ms" % home["elapsed_ms"])
    else:
        out["homepage"] = item("fail", hv, "首页不可用：%s" % (home["error"] or home["status"]))

    origin = _origin(final)
    polite_sleep()
    rob = get(origin + "/robots.txt")
    verdicts = robots_verdicts(rob["status"], rob["text"], final)
    out["robots"] = item("pass" if verdicts["source"] == "ok" else "warn",
                         {"url": origin + "/robots.txt", "status": rob["status"], "source": verdicts["source"]},
                         verdicts["detail"])
    crawlers = {}
    for c in AI_CRAWLERS:
        v = verdicts["bots"][c["name"]]
        value = dict(v, purpose=c["purpose"], market=c["market"], owner=c["owner"])
        if v["allowed"]:
            crawlers[c["name"]] = item("pass", value, "放行")
        elif c["purpose"] == "training":
            crawlers[c["name"]] = item("warn", value, "拦截训练爬虫：可接受，不影响 AI 搜索实时引用，但影响模型对品牌的先验认知")
        else:
            crawlers[c["name"]] = item("fail", value, "拦截检索/用户触发爬虫：该 AI 搜索无法抓取本站（P0）")
    out["ai_crawlers"] = crawlers

    if home["status"] == 200:
        out["ua_blocking"] = ua_block_check(final, lambda ua: get(final, ua=ua))
    else:
        out["ua_blocking"] = {}

    sm = parse_sitemaps(rob["text"] if verdicts["source"] == "ok" else None, get, origin=origin)
    out["sitemap"] = item("pass" if sm["count"] else "warn", sm,
                          "sitemap 共 %d 个 URL" % sm["count"] if sm["count"] else "未找到可用 sitemap")

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
    noindex = [m for m in parser.meta_robots if "noindex" in m.lower() or "none" in m.lower().split(": ")[-1]]
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
    out["llms_txt"] = item("pass", has_llms, "仅记录：llms.txt 对 AI 引用无可测效果（E10），不作为建议重点")

    m = _ICP.search(extract_text(home["text"] or "") + (home["text"] or ""))
    out["icp"] = item("pass", m.group(0), "首页展示 ICP 备案号") if m else item(
        "warn", None, "首页未找到 ICP 备案号（仅国内市场相关）")
    others = _other_domains(final, parser)
    out["other_domains"] = item("pass", others, "发现疑似同品牌其他域名，可另行审计" if others else "未发现")
    return out


def main():
    args = base_argparser(__doc__.splitlines()[0]).parse_args()
    emit(run(args.url, args.proxy, args.timeout), args.out)


if __name__ == "__main__":
    main()
