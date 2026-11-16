import gzip
import unittest

from helpers import fixture_bytes, serve

import _common
from _common import MAX_BYTES, count_words, decode_body, extract_text, fetch


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


class TextTests(unittest.TestCase):
    def test_extract_text_strips_chrome(self):
        text = extract_text(fixture_bytes("article.html").decode("utf-8"))
        self.assertIn("BODY_PARAGRAPH", text)
        for junk in ("HEADER_TEXT", "NAV_TEXT", "FOOTER_TEXT", "NOSCRIPT_TEXT", "NAVSECRET", "color:red"):
            self.assertNotIn(junk, text)

    def test_count_words_mixed(self):
        self.assertEqual(count_words("GEO 优化指南 for AI search"), 8)

    def test_item_shape(self):
        self.assertEqual(_common.item("pass", 1, "ok"), {"status": "pass", "value": 1, "detail": "ok"})


if __name__ == "__main__":
    unittest.main()
