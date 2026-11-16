import gzip
import unittest

from helpers import serve

import crawl_check
from crawl_check import AI_CRAWLERS, parse_sitemaps, robots_verdicts, run, ua_block_check
from _common import fetch

EXPECTED = {
    "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "Claude-User",
    "PerplexityBot", "Perplexity-User", "Google-Extended", "Googlebot", "Bingbot",
    "Applebot-Extended", "Meta-ExternalAgent", "CCBot", "Amazonbot", "DuckAssistBot",
    "Bytespider", "Baiduspider", "Sogou web spider", "YisouSpider", "360Spider", "PetalBot",
}
SITE = "https://example.com/"
HTML = {"Content-Type": "text/html; charset=utf-8"}
TXT = {"Content-Type": "text/plain"}
XML = {"Content-Type": "application/xml"}


def setUpModule():
    crawl_check.polite_sleep = lambda *a, **k: None


class RobotsTests(unittest.TestCase):
    def test_robots_blocks_gptbot_only(self):
        r = robots_verdicts(200, "User-agent: GPTBot\nDisallow: /\n", SITE)
        self.assertEqual(r["source"], "ok")
        self.assertFalse(r["bots"]["GPTBot"]["allowed"])
        self.assertEqual(r["bots"]["GPTBot"]["matched_group"], "specific")
        self.assertTrue(r["bots"]["OAI-SearchBot"]["allowed"])

    def test_robots_wildcard_block(self):
        r = robots_verdicts(200, "User-agent: *\nDisallow: /\n", SITE)
        for name, v in r["bots"].items():
            self.assertFalse(v["allowed"], name)
            self.assertEqual(v["matched_group"], "wildcard", name)

    def test_robots_missing_404(self):
        r = robots_verdicts(404, "not found", SITE)
        self.assertEqual(r["source"], "missing")
        self.assertTrue(all(v["allowed"] for v in r["bots"].values()))

    def test_robots_soft404_html(self):
        r = robots_verdicts(200, "  <!doctype html><html><body>Disallow: /</body></html>", SITE)
        self.assertEqual(r["source"], "soft404")
        self.assertTrue(all(v["allowed"] for v in r["bots"].values()))

    def test_robots_case_insensitive_token(self):
        r = robots_verdicts(200, "User-agent: gptbot\nDisallow: /\n", SITE)
        self.assertFalse(r["bots"]["GPTBot"]["allowed"])
        self.assertEqual(r["bots"]["GPTBot"]["matched_group"], "specific")

    def test_crawler_list_complete(self):
        names = {c["name"] for c in AI_CRAWLERS}
        self.assertTrue(EXPECTED <= names, EXPECTED - names)
        for c in AI_CRAWLERS:
            self.assertIn(c["purpose"], {"training", "search", "user"})
            self.assertIn(c["market"], {"global", "cn"})


class SitemapTests(unittest.TestCase):
    def test_sitemap_index_recursion(self):
        holder = {}

        def index(_h):
            b = holder["base"]
            body = ('<?xml version="1.0"?><sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                    '<sitemap><loc>%s/a.xml</loc></sitemap><sitemap><loc>%s/b.xml.gz</loc></sitemap>'
                    '</sitemapindex>' % (b, b))
            return 200, XML, body.encode()

        a = ('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>https://e.com/1</loc></url>'
             '<url><loc>https://e.com/2</loc></url></urlset>').encode()
        b = gzip.compress(b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                          b'<url><loc>https://e.com/3</loc></url></urlset>')
        base, stop = serve({"/index.xml": index, "/a.xml": (200, XML, a),
                            "/b.xml.gz": (200, {"Content-Type": "application/gzip"}, b)})
        holder["base"] = base
        try:
            r = parse_sitemaps("Sitemap: %s/index.xml\n" % base, lambda u: fetch(u))
        finally:
            stop()
        self.assertEqual(r["count"], 3)
        self.assertEqual(sorted(r["urls"]), ["https://e.com/1", "https://e.com/2", "https://e.com/3"])


class UABlockTests(unittest.TestCase):
    def _serve(self, blocked):
        def home(headers):
            if blocked(headers.get("User-Agent", "")):
                return 403, HTML, b"<html>Forbidden</html>"
            return 200, HTML, b"<html><body>ok</body></html>"
        return serve({"/": home})

    def test_ua_suspect(self):
        base, stop = self._serve(lambda ua: "GPTBot" in ua or "OAI-SearchBot" in ua)
        try:
            r = ua_block_check(base + "/", lambda ua: fetch(base + "/", ua=ua))
        finally:
            stop()
        self.assertEqual(r["OAI-SearchBot"]["status"], "suspect")
        self.assertEqual(r["PerplexityBot"]["status"], "pass")

    def test_ua_all_blocked_warn(self):
        base, stop = self._serve(lambda ua: True)
        try:
            r = ua_block_check(base + "/", lambda ua: fetch(base + "/", ua=ua))
        finally:
            stop()
        self.assertEqual(r["OAI-SearchBot"]["status"], "warn")


class RunTests(unittest.TestCase):
    def test_run_uses_final_origin(self):
        base2, stop2 = serve({"/": (200, HTML, b"<html><body>site2</body></html>"),
                              "/robots.txt": (200, TXT, b"User-agent: GPTBot\nDisallow: /\n")})
        base1, stop1 = serve({"/": (301, {"Location": base2 + "/"}, b""),
                              "/robots.txt": (200, TXT, b"User-agent: *\nAllow: /\n")})
        try:
            r = run(base1 + "/", None, 5)
        finally:
            stop1()
            stop2()
        self.assertTrue(r["final_url"].startswith(base2))
        self.assertEqual(r["ai_crawlers"]["GPTBot"]["value"]["allowed"], False)

    def _site(self, home_html):
        return serve({
            "/": (200, HTML, home_html.encode("utf-8")),
            "/robots.txt": (200, TXT, b"User-agent: *\nAllow: /\n"),
            "/llms.txt": (200, TXT, b"# Example\n"),
        })

    def test_icp_detected(self):
        base, stop = self._site("<html><body><footer>粤ICP备12345678号-1</footer></body></html>")
        try:
            r = run(base + "/", None, 5)
        finally:
            stop()
        self.assertEqual(r["icp"]["status"], "pass")
        self.assertEqual(r["icp"]["value"], "粤ICP备12345678号-1")

    def test_run_shape(self):
        base, stop = self._site('<html><head><link rel="canonical" href="/"></head><body>hi</body></html>')
        try:
            r = run(base + "/", None, 5)
        finally:
            stop()
        self.assertEqual(set(r), {"target", "final_url", "fetched_at", "homepage", "robots", "ai_crawlers",
                                  "ua_blocking", "sitemap", "canonical", "meta_robots", "x_robots_tag",
                                  "https", "llms_txt", "icp", "other_domains"})
        self.assertIs(r["llms_txt"]["value"], True)
        self.assertEqual(r["homepage"]["status"], "pass")


if __name__ == "__main__":
    unittest.main()
