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
        r = compare("<html></html>", "<html></html>")
        self.assertEqual(r["ratio"], 1.0)
        self.assertEqual(r["check"]["status"], "unknown")

    def test_challenge_page_unknown(self):
        page = b"<html><head><title>Just a moment...</title></head><body>checking</body></html>"
        base, stop = serve({"/": (403, {"Content-Type": "text/html", "cf-mitigated": "challenge"}, page)})
        try:
            r = diff_url(base + "/", None, 5, browser="/usr/bin/true")
        finally:
            stop()
        self.assertEqual(r["check"]["status"], "unknown")


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

    def test_render_survives_profile_cleanup_error(self):
        """Chrome 退出后仍在写 profile 时，清理失败不能让 render 崩溃。"""
        import shutil
        real_rmtree = shutil.rmtree

        def fake_run(cmd, **kw):
            return mock.Mock(returncode=0, stdout=b"<html><body>dom</body></html>")

        def strict_rmtree(path, ignore_errors=False, **kw):
            if not ignore_errors:
                raise OSError(39, "Directory not empty")
            real_rmtree(path, ignore_errors=True)

        with mock.patch("render_diff.subprocess.run", side_effect=fake_run), \
             mock.patch("render_diff.shutil.rmtree", side_effect=strict_rmtree), \
             mock.patch("tempfile.TemporaryDirectory.cleanup", side_effect=OSError(39, "Directory not empty")):
            self.assertIn("dom", render("http://x/", "/usr/bin/google-chrome", None, 5))

    def test_render_passes_lang(self):
        captured = {}

        def fake_run(cmd, **kw):
            captured["cmd"] = cmd
            return mock.Mock(returncode=0, stdout=b"<html><body>dom</body></html>")

        with mock.patch("render_diff.subprocess.run", side_effect=fake_run):
            render("http://x/", "/usr/bin/google-chrome", None, 5, lang="ja-JP")
        self.assertIn("--lang=ja-JP", captured["cmd"])

    def test_diff_url_lang_header(self):
        seen = []

        def page(h):
            seen.append(h.get("Accept-Language", ""))
            return 200, {"Content-Type": "text/html"}, b"<p>x</p>"

        base, stop = serve({"/": page})
        try:
            diff_url(base + "/", None, 5, browser="/usr/bin/true", lang="de-DE")
        finally:
            stop()
        self.assertTrue(seen and seen[0].startswith("de-DE"))

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
