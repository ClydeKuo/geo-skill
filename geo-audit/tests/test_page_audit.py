import unittest

from helpers import fixture_bytes, serve

import page_audit
from page_audit import audit_html, audit_url

URL = "https://www.lock-example.com.cn/guide"


def setUpModule():
    page_audit.polite_sleep = lambda *a, **k: None


class AuditHtmlTests(unittest.TestCase):
    def test_rich_page_counts(self):
        r = audit_html(fixture_bytes("rich_page.html").decode("utf-8"), URL)
        self.assertEqual(r["title"], "智能门锁选购指南 2026")
        self.assertEqual(r["lang"], "zh-CN")
        self.assertEqual(r["h1_count"], 1)
        self.assertEqual(r["tables"], 1)
        self.assertEqual(r["lists"], 2)
        self.assertGreaterEqual(r["numbers"], 3)
        self.assertGreaterEqual(r["dates"], 1)
        self.assertEqual(r["external_links"], 2)
        self.assertEqual(r["blockquotes"], 1)
        self.assertIn("Article", r["jsonld_types"])
        self.assertIn("FAQPage", r["jsonld_types"])
        self.assertEqual(r["author"], "张三")
        self.assertEqual(r["date_modified"], "2026-10-01")
        self.assertEqual([h["level"] for h in r["headings"]], [1, 2, 3, 2, 3, 2])
        self.assertEqual(r["heading_skips"], 0)
        self.assertEqual(r["og"].get("og:title"), "智能门锁选购指南")

    def test_hardware_units_count_as_numbers(self):
        html = "<p>打印速度 600 mm/s，热床 110 ℃，喷嘴 300°C，功率 350 W，层厚 50 μm，换料 6 s。</p>"
        self.assertGreaterEqual(audit_html(html, URL)["numbers"], 6)

    def test_chrome_links_and_headings_excluded(self):
        html = ("<header><h6>菜单</h6><a href='https://facebook.com/x'>fb</a></header>"
                "<nav><a href='https://twitter.com/x'>tw</a><h4>导航</h4></nav>"
                "<main><h1>标题</h1><h2>小节</h2><p><a href='https://www.samr.gov.cn/a'>来源</a></p></main>"
                "<footer><h6>关于</h6><a href='https://youtube.com/x'>yt</a></footer>")
        r = audit_html(html, URL)
        self.assertEqual(r["external_links"], 1)
        self.assertEqual([h["text"] for h in r["headings"]], ["标题", "小节"])
        self.assertEqual(r["heading_skips"], 0)

    def test_canonical(self):
        r = audit_html('<head><link rel="canonical" href="/cn/guide"></head><p>x</p>', URL)
        self.assertEqual(r["canonical"], "https://www.lock-example.com.cn/cn/guide")

    def test_heading_skip(self):
        self.assertEqual(audit_html("<h2>a</h2><h4>b</h4>", URL)["heading_skips"], 1)

    def test_thin_page(self):
        r = audit_html(fixture_bytes("thin_page.html").decode("utf-8"), URL)
        self.assertLess(r["word_count"], 20)
        self.assertEqual(r["h1_count"], 0)

    def test_bad_jsonld_ignored(self):
        r = audit_html('<script type="application/ld+json">{bad json</script><p>x</p>', URL)
        self.assertEqual(r["jsonld_types"], [])


class AuditUrlTests(unittest.TestCase):
    def test_audit_url_pdf_unknown(self):
        base, stop = serve({"/a.pdf": (200, {"Content-Type": "application/pdf"}, b"%PDF-1.4")})
        try:
            r = audit_url(base + "/a.pdf", None, 5)
        finally:
            stop()
        self.assertEqual(r["check"]["status"], "unknown")
        self.assertIsNone(r["result"])

    def test_audit_url_challenge_unknown(self):
        page = b"<html><head><title>Just a moment...</title></head><body>checking</body></html>"
        base, stop = serve({"/": (200, {"Content-Type": "text/html"}, page)})
        try:
            r = audit_url(base + "/", None, 5)
        finally:
            stop()
        self.assertEqual(r["check"]["status"], "unknown")

    def test_audit_url_ok(self):
        base, stop = serve({"/": (200, {"Content-Type": "text/html; charset=utf-8"}, fixture_bytes("rich_page.html"))})
        try:
            r = audit_url(base + "/", None, 5)
        finally:
            stop()
        self.assertEqual(r["check"]["status"], "pass")
        self.assertEqual(r["result"]["h1_count"], 1)


if __name__ == "__main__":
    unittest.main()
