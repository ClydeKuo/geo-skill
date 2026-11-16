import gzip
import unittest

from helpers import fixture_bytes, serve

import _common
import json
import os
import subprocess
import sys

from _common import MAX_BYTES, count_words, decode_body, extract_text, fetch, normalize_url


class DecodeTests(unittest.TestCase):
    def test_decode_gbk_meta(self):
        self.assertIn("智能家居解决方案", decode_body(fixture_bytes("gbk.html"), "text/html"))

    def test_decode_header_charset_wins(self):
        raw = "<p>中文内容测试</p>".encode("gb2312")
        self.assertIn("中文内容测试", decode_body(raw, "text/html; charset=gb2312"))


class FetchTests(unittest.TestCase):
    def setUp(self):
        big = b"<html><body>" + b"a" * (6 * 1024 * 1024) + b"</body></html>"
        self.base, self.stop = serve({
            "/gz": (200, {"Content-Type": "text/html; charset=utf-8", "Content-Encoding": "gzip"},
                    gzip.compress("<p>压缩正文</p>".encode("utf-8"))),
            "/old": (301, {"Location": "/new"}, b""),
            "/new": (200, {"Content-Type": "text/html"}, b"<p>new</p>"),
            "/big": (200, {"Content-Type": "text/html"}, big),
            "/doc.pdf": (200, {"Content-Type": "application/pdf"}, b"%PDF-1.4"),
        })

    def tearDown(self):
        self.stop()

    def test_fetch_gzip(self):
        r = fetch(self.base + "/gz")
        self.assertIn("压缩正文", r["text"])

    def test_fetch_redirect_final_url(self):
        r = fetch(self.base + "/old")
        self.assertEqual(r["status"], 200)
        self.assertTrue(r["final_url"].endswith("/new"))

    def test_fetch_404_not_error(self):
        r = fetch(self.base + "/missing")
        self.assertEqual(r["status"], 404)
        self.assertIsNone(r["error"])

    def test_fetch_connection_error(self):
        r = fetch("http://127.0.0.1:1/", timeout=3)
        self.assertIsNone(r["status"])
        self.assertTrue(r["error"])

    def test_fetch_truncates(self):
        r = fetch(self.base + "/big")
        self.assertTrue(r["truncated"])
        self.assertEqual(r["bytes"], MAX_BYTES)

    def test_fetch_non_html(self):
        r = fetch(self.base + "/doc.pdf")
        self.assertIsNone(r["text"])
        self.assertEqual(r["content_type"], "application/pdf")


class RobustnessTests(unittest.TestCase):
    def test_normalize_url(self):
        self.assertEqual(normalize_url("example.com"), "https://example.com")
        self.assertEqual(normalize_url(" http://a.com/x "), "http://a.com/x")

    def test_fetch_bad_url_no_raise(self):
        r = fetch("example.com")
        self.assertIsNone(r["status"])
        self.assertTrue(r["error"])

    def test_fetch_non_ascii_path(self):
        base, stop = serve({"/%E8%B7%AF%E5%BE%84": (200, {"Content-Type": "text/html"}, b"<p>ok</p>")})
        try:
            r = fetch(base + "/路径")
        finally:
            stop()
        self.assertEqual(r["status"], 200)

    def test_cli_never_tracebacks(self):
        scripts = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
        for script in ("crawl_check.py", "page_audit.py", "render_diff.py"):
            proc = subprocess.run([sys.executable, os.path.join(scripts, script), "http://[bad", "--timeout", "2"],
                                  capture_output=True, text=True, timeout=60)
            self.assertEqual(proc.returncode, 0, script + proc.stderr)
            self.assertNotIn("Traceback", proc.stderr, script)
            json.loads(proc.stdout)


class TextTests(unittest.TestCase):
    def test_extract_text_keeps_article_header(self):
        html = "<article><header><h1>Title</h1><p>By Alice, 2024-01-01</p></header><p>body</p></article>"
        text = extract_text(html)
        self.assertIn("2024-01-01", text)
        self.assertIn("Title", text)

    def test_extract_text_strips_chrome(self):
        text = extract_text(fixture_bytes("article.html").decode("utf-8"))
        self.assertIn("BODY_PARAGRAPH", text)
        for junk in ("HEADER_TEXT", "NAV_TEXT", "FOOTER_TEXT", "NOSCRIPT_TEXT", "NAVSECRET", "color:red"):
            self.assertNotIn(junk, text)

    def test_extract_text_skips_textarea(self):
        html = '<p>正文</p><textarea style="display:none">&lt;style&gt;body{color:red}&lt;/style&gt;</textarea>'
        text = extract_text(html)
        self.assertIn("正文", text)
        self.assertNotIn("color", text)

    def test_count_words_mixed(self):
        self.assertEqual(count_words("GEO 优化指南 for AI search"), 8)

    def test_item_shape(self):
        self.assertEqual(_common.item("pass", 1, "ok"), {"status": "pass", "value": 1, "detail": "ok"})


if __name__ == "__main__":
    unittest.main()


import email.utils
import time as _time
from unittest import mock as _mock

from _common import accept_language, current_interval, parse_retry_after, reset_interval
import _common as _c


class LangTests(unittest.TestCase):
    def test_accept_language_values(self):
        self.assertEqual(accept_language(None), "zh-CN,zh;q=0.9,en;q=0.8")
        self.assertEqual(accept_language("ja-JP"), "ja-JP,ja;q=0.9,en;q=0.5")
        self.assertEqual(accept_language("es"), "es,en;q=0.5")

    def test_fetch_sends_lang(self):
        base, stop = serve({"/": lambda h: (200, {"Content-Type": "text/plain"},
                                            h.get("Accept-Language", "").encode())})
        try:
            r = fetch(base + "/", lang="ko-KR")
        finally:
            stop()
        self.assertTrue(r["text"].startswith("ko-KR,ko;q=0.9"))


class RateLimitTests(unittest.TestCase):
    def setUp(self):
        reset_interval()
        self.sleeps = []
        p = _mock.patch.object(_c.time, "sleep", side_effect=lambda s: self.sleeps.append(s))
        p.start()
        self.addCleanup(p.stop)
        self.addCleanup(reset_interval)

    def _counting(self, responses):
        calls = []

        def route(_h):
            calls.append(1)
            return responses[min(len(calls), len(responses)) - 1]
        return route, calls

    def test_parse_retry_after(self):
        self.assertEqual(parse_retry_after("5"), 5.0)
        self.assertEqual(parse_retry_after("abc"), 10.0)
        self.assertEqual(parse_retry_after(None), 10.0)
        self.assertEqual(parse_retry_after("-3"), 0.0)
        now = 1_800_000_000.0
        date = email.utils.formatdate(now + 30, usegmt=True)
        self.assertEqual(parse_retry_after(date, now=now), 30.0)

    def test_429_retry_once_then_ok(self):
        route, calls = self._counting([(429, {"Retry-After": "2"}, b"slow"),
                                       (200, {"Content-Type": "text/html"}, b"<p>ok</p>")])
        base, stop = serve({"/": route})
        try:
            r = fetch(base + "/")
        finally:
            stop()
        self.assertEqual(r["status"], 200)
        self.assertFalse(r["rate_limited"])
        self.assertIn(2.0, self.sleeps)

    def test_429_twice_returns_429(self):
        route, calls = self._counting([(429, {"Retry-After": "1"}, b"slow")])
        base, stop = serve({"/": route})
        try:
            r = fetch(base + "/")
        finally:
            stop()
        self.assertEqual(r["status"], 429)
        self.assertTrue(r["rate_limited"])
        self.assertEqual(len(calls), 2)

    def test_retry_after_too_long_no_wait(self):
        route, calls = self._counting([(429, {"Retry-After": "120"}, b"slow")])
        base, stop = serve({"/": route})
        try:
            r = fetch(base + "/")
        finally:
            stop()
        self.assertEqual(r["status"], 429)
        self.assertTrue(r["rate_limited"])
        self.assertEqual(len(calls), 1)
        self.assertFalse([s for s in self.sleeps if s >= 60])

    def test_503_without_retry_after_not_retried(self):
        route, calls = self._counting([(503, {}, b"down")])
        base, stop = serve({"/": route})
        try:
            fetch(base + "/")
        finally:
            stop()
        self.assertEqual(len(calls), 1)

    def test_challenge_503_not_retried(self):
        route, calls = self._counting([(503, {"Retry-After": "1", "cf-mitigated": "challenge"}, b"x")])
        base, stop = serve({"/": route})
        try:
            fetch(base + "/")
        finally:
            stop()
        self.assertEqual(len(calls), 1)

    def test_interval_doubles_and_caps(self):
        _c._note_rate_limited()
        self.assertEqual(current_interval(), 2.0)
        for _ in range(4):
            _c._note_rate_limited()
        self.assertEqual(current_interval(), 10.0)
