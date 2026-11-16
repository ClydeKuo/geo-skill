"""GEO 审计脚本共享模块：抓取、解码、正文提取、计字、结果格式。

只依赖 Python 3 标准库。
"""
import argparse
import email.utils
import gzip
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib
from html.parser import HTMLParser

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
)
MAX_BYTES = 5 * 1024 * 1024

_last_request = [0.0]
DEFAULT_INTERVAL = 1.0
MAX_INTERVAL = 10.0
DEFAULT_RETRY_AFTER = 10.0
MAX_RETRY_WAIT = 30.0  # 超过则不等待：避免单个脚本因 Retry-After: 60 累计等待超过 shell 超时
_interval = [DEFAULT_INTERVAL]
_retry_disabled = [False]  # 本进程内一旦出现最终仍被限流的请求，后续不再等待重试


def current_interval():
    return _interval[0]


def reset_interval():
    """仅供测试：恢复默认请求间隔与重试状态。"""
    _interval[0] = DEFAULT_INTERVAL
    _retry_disabled[0] = False


def _note_rate_limited():
    """遇到 429 后请求间隔翻倍（上限 MAX_INTERVAL），本进程内不回落。"""
    _interval[0] = min(_interval[0] * 2, MAX_INTERVAL)


def polite_sleep(seconds=None):
    """保证相邻请求间隔至少 max(seconds, 当前自适应间隔) 秒。"""
    gap = max(seconds or 0, current_interval())
    wait = _last_request[0] + gap - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    _last_request[0] = time.monotonic()


def parse_retry_after(value, now=None):
    """Retry-After（秒数或 HTTP 日期）→ 等待秒数；缺省或无法解析时 DEFAULT_RETRY_AFTER。"""
    if value is None:
        return DEFAULT_RETRY_AFTER
    value = value.strip()
    try:
        return max(float(value), 0.0)
    except ValueError:
        pass
    try:
        dt = email.utils.parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        return DEFAULT_RETRY_AFTER
    if dt is None:
        return DEFAULT_RETRY_AFTER
    now = time.time() if now is None else now
    return max(round(dt.timestamp() - now, 3), 0.0)


def accept_language(lang):
    """按目标语言生成 Accept-Language；None 时为默认中文优先。"""
    if not lang:
        return "zh-CN,zh;q=0.9,en;q=0.8"
    primary = lang.split("-")[0]
    if primary == lang:
        return "%s,en;q=0.5" % lang
    return "%s,%s;q=0.9,en;q=0.5" % (lang, primary)


def item(status, value=None, detail=""):
    return {"status": status, "value": value, "detail": detail}


_META_CHARSET = re.compile(rb"""<meta[^>]+charset\s*=\s*["']?\s*([A-Za-z0-9_\-]+)""", re.I)


def _charset_from_content_type(content_type):
    m = re.search(r"charset\s*=\s*[\"']?([A-Za-z0-9_\-]+)", content_type or "", re.I)
    return m.group(1) if m else None


def _normalize_charset(name):
    name = name.lower()
    # GBK / GB2312 页面常混入 GB18030 字符，统一用超集解码
    if name in ("gbk", "gb2312", "gb_2312", "x-gbk", "cp936"):
        return "gb18030"
    return name


def decode_body(raw, content_type):
    """按 HTTP charset → <meta charset> → utf-8 → gb18030 顺序解码。"""
    candidates = []
    cs = _charset_from_content_type(content_type)
    if cs:
        candidates.append(cs)
    m = _META_CHARSET.search(raw[:4096])
    if m:
        candidates.append(m.group(1).decode("ascii", "ignore"))
    candidates += ["utf-8", "gb18030"]
    for name in candidates:
        try:
            return raw.decode(_normalize_charset(name))
        except (LookupError, UnicodeDecodeError):
            continue
    return raw.decode("utf-8", "replace")


def _decompress(raw, encoding):
    encoding = (encoding or "").lower()
    try:
        if "gzip" in encoding:
            return gzip.decompress(raw)
        if "deflate" in encoding:
            try:
                return zlib.decompress(raw)
            except zlib.error:
                return zlib.decompress(raw, -zlib.MAX_WBITS)
    except (OSError, EOFError, zlib.error):
        return raw
    return raw


def _is_text(content_type):
    ct = (content_type or "").lower()
    return ct.startswith("text/") or "html" in ct or "xml" in ct or "json" in ct or ct == ""


def normalize_url(url):
    """补全协议：用户常输入 example.com。"""
    url = (url or "").strip()
    if not re.match(r"^[A-Za-z][A-Za-z0-9+.\-]*://", url):
        url = "https://" + url
    return url


def _ascii_url(url):
    """把中文路径 / IDN 主机名转换为可请求的 ASCII URL。"""
    p = urllib.parse.urlsplit(url)
    host = p.hostname or ""
    try:
        host = host.encode("idna").decode("ascii")
    except UnicodeError:
        pass
    netloc = host + (":%d" % p.port if p.port else "")
    if p.username:
        netloc = "%s@%s" % (p.username + (":" + p.password if p.password else ""), netloc)
    path = urllib.parse.quote(p.path, safe="/%:@!$&'()*+,;=-._~")
    query = urllib.parse.quote(p.query, safe="=&%:@!$'()*+,;/?-._~")
    return urllib.parse.urlunsplit((p.scheme, netloc, path, query, ""))


def fetch(url, ua=BROWSER_UA, proxy=None, timeout=10, force_text=False, lang=None):
    """GET 一个 URL。HTTP 错误码照实返回；网络错误或非法 URL 时 status=None、error 为原因，不抛异常。

    force_text=True 时不论 Content-Type 都解码为文本（用于 robots.txt 等）。
    lang 为 BCP 47 标签时据此设置 Accept-Language。
    遇到 429、或带 Retry-After 的 503（挑战页除外）时，按 Retry-After 等待后重试一次；
    Retry-After 超过 MAX_RETRY_WAIT 不等待。结果中 rate_limited=True 表示最终仍被限流。
    """
    r = _fetch_once(url, ua, proxy, timeout, force_text, lang)
    if not _should_retry(r):
        return r
    if r["status"] == 429:
        _note_rate_limited()
    wait = parse_retry_after(r["headers"].get("retry-after"))
    if wait > MAX_RETRY_WAIT or _retry_disabled[0]:
        r["rate_limited"] = True
        _retry_disabled[0] = True
        return r
    time.sleep(wait)
    r2 = _fetch_once(url, ua, proxy, timeout, force_text, lang)
    if _should_retry(r2):
        if r2["status"] == 429:
            _note_rate_limited()
        r2["rate_limited"] = True
        _retry_disabled[0] = True
    return r2


def _should_retry(r):
    if is_challenge(r):
        return False
    return r["status"] == 429 or (r["status"] == 503 and "retry-after" in r["headers"])


def _fetch_once(url, ua, proxy, timeout, force_text, lang):
    result = {"url": url, "final_url": url, "status": None, "headers": {}, "content_type": "",
              "text": None, "bytes": 0, "elapsed_ms": 0, "truncated": False, "error": None,
              "rate_limited": False}
    start = time.monotonic()
    try:
        handlers = []
        if proxy:
            handlers.append(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
        opener = urllib.request.build_opener(*handlers)
        req = urllib.request.Request(_ascii_url(url), headers={
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Accept-Language": accept_language(lang),
        })
        try:
            resp = opener.open(req, timeout=timeout)
        except urllib.error.HTTPError as e:
            resp = e
        with resp:
            raw = resp.read(MAX_BYTES + 1)
            result["status"] = resp.status if hasattr(resp, "status") else resp.code
            result["final_url"] = resp.geturl() or url
            headers = {k.lower(): v for k, v in resp.headers.items()}
    except Exception as e:  # 网络错误、超时、SSL 等
        result["error"] = "%s: %s" % (type(e).__name__, e)
        result["elapsed_ms"] = int((time.monotonic() - start) * 1000)
        return result
    result["elapsed_ms"] = int((time.monotonic() - start) * 1000)
    if len(raw) > MAX_BYTES:
        raw = raw[:MAX_BYTES]
        result["truncated"] = True
    result["bytes"] = len(raw)
    result["headers"] = headers
    ct = headers.get("content-type", "")
    result["content_type"] = ct.split(";")[0].strip().lower() if ct else ""
    body = _decompress(raw, headers.get("content-encoding"))
    is_gzip_file = body[:2] == b"\x1f\x8b"
    if is_gzip_file:  # 如 sitemap.xml.gz：文件本身是 gzip
        try:
            body = gzip.decompress(body)
        except (OSError, EOFError):
            is_gzip_file = False
    if force_text or _is_text(ct) or is_gzip_file:
        result["text"] = decode_body(body, ct)
    return result


_SKIP_TAGS = {"script", "style", "noscript", "template", "svg", "nav", "textarea"}
_PAGE_CHROME = {"header", "footer"}  # 只在 main/article 之外才视为页面外壳
_BLOCK_TAGS = {"p", "div", "section", "article", "main", "li", "ul", "ol", "table", "tr", "td", "th",
               "h1", "h2", "h3", "h4", "h5", "h6", "br", "blockquote", "pre", "dd", "dt", "figcaption"}
_VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_stack = []
        self.content_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("main", "article") and not self.skip_stack:
            self.content_depth += 1
        if tag in _SKIP_TAGS or (tag in _PAGE_CHROME and self.content_depth == 0):
            self.skip_stack.append(tag)
        elif tag in _BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if self.skip_stack and tag == self.skip_stack[-1]:
            self.skip_stack.pop()
        elif tag in ("main", "article") and not self.skip_stack and self.content_depth:
            self.content_depth -= 1
        elif tag in _BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data):
        if not self.skip_stack:
            self.parts.append(data)


def extract_text(html):
    p = _TextExtractor()
    try:
        p.feed(html or "")
        p.close()
    except Exception:
        pass
    text = "".join(p.parts)
    lines = [re.sub(r"[ \t\r\f\v ]+", " ", ln).strip() for ln in text.split("\n")]
    return "\n".join(ln for ln in lines if ln)


_CJK = re.compile(r"[㐀-䶿一-鿿豈-﫿぀-ヿ가-힯]")
_WORD = re.compile(r"[A-Za-z0-9]+")


def count_words(text):
    """CJK 字符每字计 1，其余按字母数字词计。"""
    text = text or ""
    return len(_CJK.findall(text)) + len(_WORD.findall(text))


def base_argparser(description):
    ap = argparse.ArgumentParser(description=description)
    ap.add_argument("url")
    ap.add_argument("--proxy", default=None, help="HTTP 代理，如 http://proxy.example:8080")
    ap.add_argument("--timeout", type=float, default=10)
    ap.add_argument("--out", default=None, help="同时写入该 JSON 文件")
    return ap


def emit(result, out=None):
    data = json.dumps(result, ensure_ascii=False, indent=2)
    if out:
        with open(out, "w", encoding="utf-8") as f:
            f.write(data)
    sys.stdout.write(data + "\n")


_MULTI_SUFFIX = {"com.cn", "net.cn", "org.cn", "gov.cn", "edu.cn", "ac.cn", "co.uk", "org.uk",
                 "com.hk", "com.tw", "co.jp", "com.au", "com.sg", "co.kr"}


def registrable_domain(host):
    """近似的注册域：默认取后两段，常见二级后缀取后三段。"""
    host = (host or "").lower().strip(".").split(":")[0]
    parts = host.split(".")
    if len(parts) >= 3 and ".".join(parts[-2:]) in _MULTI_SUFFIX:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


# 只匹配挑战页/验证页本身的特征。注意：Cloudflare 会在正常页面注入
# /cdn-cgi/challenge-platform/scripts/jsd/main.js，不能把 "challenge-platform" 当挑战特征。
_CHALLENGE_TITLE = re.compile(
    r"<title>\s*(?:just a moment|attention required|access denied|请稍候|安全验证|人机验证|验证码)", re.I)
_CHALLENGE_BODY = re.compile(r"_cf_chl_opt|cf-chl-widget|challenges\.cloudflare\.com/turnstile", re.I)


def is_challenge(resp):
    """响应是否为 WAF / CDN 的挑战或验证页。"""
    if "challenge" in (resp.get("headers") or {}).get("cf-mitigated", "").lower():
        return True
    text = resp.get("text") or ""
    return bool(_CHALLENGE_TITLE.search(text) or _CHALLENGE_BODY.search(text))


def safe_main(main):
    """脚本入口保护：任何未预料的异常都输出 unknown JSON 并以 0 退出，不打印调用栈。"""
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        emit({"error": item("unknown", None, "脚本内部错误：%s: %s" % (type(e).__name__, e))})
