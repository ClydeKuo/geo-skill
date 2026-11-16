import os
import unittest
from unittest import mock

from helpers import fixture_bytes, serve

import render_diff
from render_diff import THRESHOLD, compare, diff_url, find_browser, render

BODY = "<p>" + "智能门锁" * 75 + "</p>"  # 300 字


def setUpModule():
    render_diff.polite_sleep = lambda *a, **k: None


class CompareTests(unittest.TestCase):
    def test_threshold(self):
        self.assertEqual(THRESHOLD, 0.5)

    def test_compare_csr_fail(self):
        raw = fixture_bytes("csr_page.html").decode()
        rendered = raw.replace('<div id="app"></div>', '<div id="app"><h2>核心功能</h2>%s</div>' % BODY)
        r = compare(raw, rendered)
        self.assertEqual(r["check"]["status"], "fail")
        self.assertEqual(r["js_only_headings"], ["核心功能"])
        self.assertLess(r["ratio"], 0.5)

    def test_compare_ssr_pass(self):
        page = "<html><body><h1>t</h1>%s</body></html>" % BODY
        r = compare(page, page)
        self.assertEqual(r["ratio"], 1.0)
        self.assertEqual(r["check"]["status"], "pass")

    def test_compare_partial_warn(self):
        rendered = "<html><body><p>%s</p></body></html>" % ("字" * 100)
        raw = "<html><body><p>%s</p></body></html>" % ("字" * 60)
        self.assertEqual(compare(raw, rendered)["check"]["status"], "warn")

    def test_compare_empty_rendered(self):
        self.assertEqual(compare("<html></html>", "<html></html>")["ratio"], 1.0)


class BrowserTests(unittest.TestCase):
    def test_no_browser_unknown(self):
        base, stop = serve({"/": (200, {"Content-Type": "text/html"}, b"<p>x</p>")})
        try:
            with mock.patch.dict(os.environ, {"GEO_BROWSER": "/nonexistent/chrome"}), \
                 mock.patch("render_diff.shutil.which", return_value=None), \
                 mock.patch("render_diff.glob.glob", return_value=[]):
                self.assertIsNone(find_browser())
                r = diff_url(base + "/", None, 5)
        finally:
            stop()
        self.assertEqual(r["check"]["status"], "unknown")

    @unittest.skipUnless(find_browser(), "no browser installed")
    def test_render_real_browser(self):
        page = (b"<html><body><div id='a'></div><script>"
                b"document.getElementById('a').innerHTML='<p>hello geo</p>';</script></body></html>")
        base, stop = serve({"/": (200, {"Content-Type": "text/html"}, page)})
        try:
            html = render(base + "/", find_browser(), None, 10)
        finally:
            stop()
        self.assertIn("hello geo", html)


if __name__ == "__main__":
    unittest.main()
