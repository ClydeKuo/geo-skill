#!/usr/bin/env python3
"""无 JS 原始 HTML 与浏览器渲染后正文对比：估计不执行 JS 的 AI 爬虫能看到多少内容。

用法：python3 render_diff.py <url> [<url> ...] [--proxy URL] [--timeout 10] [--out file.json]
环境变量 GEO_BROWSER 可指定浏览器路径。
"""
import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (BROWSER_UA, base_argparser, count_words, emit, extract_text, fetch, item,  # noqa: E402
                     polite_sleep)
from page_audit import audit_html  # noqa: E402

THRESHOLD = 0.5
WARN_THRESHOLD = 0.8


def _version_key(path):
    m = re.search(r"-(\d+)", path)
    return int(m.group(1)) if m else 0


def find_browser():
    env = os.environ.get("GEO_BROWSER")
    if env and os.path.isfile(env) and os.access(env, os.X_OK):
        return env
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        path = shutil.which(name)
        if path:
            return path
    pattern = os.path.expanduser(
        "~/.cache/ms-playwright/chromium_headless_shell-*/chrome-headless-shell*/chrome-headless-shell")
    found = sorted(glob.glob(pattern), key=_version_key)
    return found[-1] if found else None


def render(url, browser, proxy=None, timeout=10):
    """用 headless 浏览器渲染页面并返回 DOM；失败返回 None。"""
    with tempfile.TemporaryDirectory(prefix="geo-chrome-") as profile:
        cmd = [browser]
        if "headless-shell" not in os.path.basename(browser) and "headless_shell" not in browser:
            cmd.append("--headless=new")
        cmd += ["--disable-gpu", "--no-sandbox", "--no-first-run", "--hide-scrollbars",
                "--user-data-dir=%s" % profile, "--user-agent=%s" % BROWSER_UA,
                "--virtual-time-budget=8000", "--dump-dom", url]
        if proxy:
            cmd.insert(1, "--proxy-server=%s" % proxy)
        try:
            proc = subprocess.run(cmd, capture_output=True, timeout=timeout + 20)
        except (subprocess.TimeoutExpired, OSError):
            return None
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    return proc.stdout.decode("utf-8", "replace")


def compare(raw_html, rendered_html):
    raw_words = count_words(extract_text(raw_html))
    rendered_words = count_words(extract_text(rendered_html))
    ratio = 1.0 if rendered_words == 0 else round(min(raw_words / rendered_words, 1.0), 3)
    raw_heads = {h["text"] for h in audit_html(raw_html, "http://x/")["headings"]}
    js_only = [h["text"] for h in audit_html(rendered_html, "http://x/")["headings"]
               if h["text"] and h["text"] not in raw_heads]
    if ratio < THRESHOLD:
        check = item("fail", ratio, "不执行 JS 时只能看到 %.0f%% 正文：主流 AI 爬虫基本看不到本页内容（P0）" % (ratio * 100))
    elif ratio < WARN_THRESHOLD:
        check = item("warn", ratio, "不执行 JS 时缺失约 %.0f%% 正文" % ((1 - ratio) * 100))
    else:
        check = item("pass", ratio, "正文基本在原始 HTML 中")
    return {"raw_words": raw_words, "rendered_words": rendered_words, "ratio": ratio,
            "js_only_headings": js_only, "check": check}


def diff_url(url, proxy=None, timeout=10, browser=None):
    browser = browser or find_browser()
    out = {"url": url}
    if not browser:
        out["check"] = item("unknown", None, "未找到 Chrome/Chromium，未检测渲染差异")
        return out
    raw = fetch(url, proxy=proxy, timeout=timeout)
    if raw["status"] != 200 or raw["text"] is None:
        out["check"] = item("unknown", None, "原始页面不可用（%s）" % (raw["error"] or raw["status"]))
        return out
    rendered = render(raw["final_url"], browser, proxy, timeout)
    if rendered is None:
        out["check"] = item("unknown", None, "浏览器渲染失败")
        return out
    out.update(compare(raw["text"], rendered))
    return out


def main():
    ap = base_argparser(__doc__.splitlines()[0])
    ap.add_argument("more_urls", nargs="*")
    args = ap.parse_args()
    browser = find_browser()
    pages = []
    for u in [args.url] + args.more_urls:
        polite_sleep()
        pages.append(diff_url(u, args.proxy, args.timeout, browser))
    emit({"browser": browser, "pages": pages}, args.out)


if __name__ == "__main__":
    main()
