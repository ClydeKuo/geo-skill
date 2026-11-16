"""GEO 审计脚本共享模块：抓取、解码、正文提取、计字、结果格式。

只依赖 Python 3 标准库。
"""
import argparse
import gzip
import json
import re
import sys
import time
import urllib.error
import urllib.request
import zlib
from html.parser import HTMLParser

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36"
)
MAX_BYTES = 5 * 1024 * 1024

_last_request = [0.0]


def polite_sleep(seconds=1.0):
    """保证相邻请求间隔至少 seconds 秒。"""
    wait = _last_request[0] + seconds - time.monotonic()
    if wait > 0:
        time.sleep(wait)
    _last_request[0] = time.monotonic()


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


def fetch(url, ua=BROWSER_UA, proxy=None, timeout=10):
    """GET 一个 URL。HTTP 错误码照实返回；网络错误 status=None。"""
    handlers = []
    if proxy:
        handlers.append(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    opener = urllib.request.build_opener(*handlers)
    req = urllib.request.Request(url, headers={
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    })
    result = {"url": url, "final_url": url, "status": None, "headers": {}, "content_type": "",
              "text": None, "bytes": 0, "elapsed_ms": 0, "truncated": False, "error": None}
    start = time.monotonic()
    try:
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
    if _is_text(ct) or is_gzip_file:
        result["text"] = decode_body(body, ct)
    return result


_SKIP_TAGS = {"script", "style", "noscript", "template", "svg", "nav", "footer", "header"}
_BLOCK_TAGS = {"p", "div", "section", "article", "main", "li", "ul", "ol", "table", "tr", "td", "th",
               "h1", "h2", "h3", "h4", "h5", "h6", "br", "blockquote", "pre", "dd", "dt", "figcaption"}
_VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.skip_stack = []

    def handle_starttag(self, tag, attrs):
        if tag in _SKIP_TAGS:
            self.skip_stack.append(tag)
        elif tag in _BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if self.skip_stack and tag == self.skip_stack[-1]:
            self.skip_stack.pop()
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
