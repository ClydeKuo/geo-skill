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


class RFC9309Tests(unittest.TestCase):
    def v(self, text, bot="GPTBot"):
        return robots_verdicts(200, text, SITE)["bots"][bot]

    def test_wildcard_path_blocks(self):
        self.assertFalse(self.v("User-agent: GPTBot\nDisallow: /*\n")["allowed"])

    def test_bare_star_blocks(self):
        self.assertFalse(self.v("User-agent: GPTBot\nDisallow: *\n")["allowed"])

    def test_allow_dollar_homepage(self):
        self.assertTrue(self.v("User-agent: GPTBot\nDisallow: /\nAllow: /$\n")["allowed"])

    def test_tie_allow_wins(self):
        self.assertTrue(self.v("User-agent: GPTBot\nDisallow: /\nAllow: /\n")["allowed"])

    def test_groups_merged(self):
        text = "User-agent: GPTBot\nDisallow: /private\n\nUser-agent: GPTBot\nDisallow: /\n"
        self.assertFalse(self.v(text)["allowed"])

    def test_bom_ignored(self):
        r = self.v("\ufeffUser-agent: *\nDisallow: /\n")
        self.assertFalse(r["allowed"])
        self.assertEqual(r["matched_group"], "wildcard")

    def test_space_before_colon(self):
        r = self.v("User-agent : GPTBot\nDisallow : /\n")
        self.assertFalse(r["allowed"])
        self.assertEqual(r["matched_group"], "specific")

    def test_specific_group_overrides_wildcard(self):
        r = self.v("User-agent: *\nDisallow: /\n\nUser-agent: GPTBot\nAllow: /\n")
        self.assertTrue(r["allowed"])
        self.assertEqual(r["matched_group"], "specific")

    def test_applebot_group_not_applebot_extended(self):
        r = self.v("User-agent: Applebot\nDisallow: /\n", bot="Applebot-Extended")
        self.assertTrue(r["allowed"])

    def test_multiple_agents_one_group(self):
        text = "User-agent: CCBot\nUser-agent: GPTBot\nDisallow: /\n"
        self.assertFalse(self.v(text)["allowed"])
        self.assertFalse(self.v(text, bot="CCBot")["allowed"])

    def test_unreachable_statuses(self):
        for status in (None, 429, 500, 503):
            r = robots_verdicts(status, None, SITE)
            self.assertEqual(r["source"], "unreachable", status)
            self.assertIsNone(r["bots"]["GPTBot"]["allowed"])


class SitemapTests(unittest.TestCase):
    def test_relative_sitemap_and_gbk(self):
        body = ('<?xml version="1.0" encoding="GBK"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                '<url><loc>https://e.com/中文</loc></url></urlset>').encode("gbk")
        base, stop = serve({"/sm.xml": (200, {"Content-Type": "application/xml"}, body)})
        try:
            r = parse_sitemaps("Sitemap: /sm.xml\n", lambda u: fetch(u), origin=base)
        finally:
            stop()
        self.assertEqual(r["urls"], ["https://e.com/中文"])

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


    def test_sitemap_nested_index_and_truncation(self):
        """两层 sitemapindex 要递归到 urlset；超过上限要标记 truncated。"""
        ns = 'xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
        holder = {}

        def idx(children):
            def h(_h):
                b = holder["base"]
                body = "<sitemapindex %s>%s</sitemapindex>" % (
                    ns, "".join("<sitemap><loc>%s%s</loc></sitemap>" % (b, c) for c in children))
                return 200, XML, body.encode()
            return h

        def urlset(n, prefix):
            body = "<urlset %s>%s</urlset>" % (ns, "".join(
                "<url><loc>https://e.com/%s/%d</loc></url>" % (prefix, i) for i in range(n)))
            return 200, XML, body.encode()

        base, stop = serve({"/root.xml": idx(["/mid.xml"]), "/mid.xml": idx(["/p.xml", "/b.xml"]),
                            "/p.xml": urlset(3, "p"), "/b.xml": urlset(2, "b")})
        holder["base"] = base
        try:
            r = parse_sitemaps("Sitemap: %s/root.xml" % base, lambda u: fetch(u))
            self.assertEqual(r["count"], 5)
            self.assertFalse(r["truncated"])
            self.assertTrue(all("/p/" in u or "/b/" in u for u in r["urls"]))
            r2 = parse_sitemaps("Sitemap: %s/root.xml" % base, lambda u: fetch(u), limit=4)
        finally:
            stop()
        self.assertEqual(r2["count"], 4)
        self.assertTrue(r2["truncated"])


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


class UANetworkErrorTests(unittest.TestCase):
    def test_ai_ua_timeout_is_unknown(self):
        def fetcher(ua):
            if "Windows" in ua:
                return {"status": 200, "text": "<html>ok</html>", "headers": {}}
            return {"status": None, "text": None, "headers": {}, "error": "timeout"}
        r = ua_block_check("http://x/", fetcher)
        self.assertEqual(r["OAI-SearchBot"]["status"], "unknown")


class CloudflareTests(unittest.TestCase):
    """正常页面里 Cloudflare 注入的 challenge-platform 脚本不能被当成挑战页。"""

    NORMAL = (b"<html><body>ok<script src='/cdn-cgi/challenge-platform/scripts/jsd/main.js'>"
              b"</script></body></html>")

    def test_injected_script_not_challenge(self):
        base, stop = serve({"/": (200, HTML, self.NORMAL)})
        try:
            r = ua_block_check(base + "/", lambda ua: fetch(base + "/", ua=ua))
        finally:
            stop()
        self.assertEqual(r["OAI-SearchBot"]["status"], "pass")

    def test_cf_challenge_is_suspect(self):
        def home(headers):
            if "Mozilla/5.0 (Windows" in headers.get("User-Agent", ""):
                return 200, HTML, self.NORMAL
            return 403, dict(HTML, **{"cf-mitigated": "challenge"}), b"<html><title>Just a moment...</title></html>"
        base, stop = serve({"/": home})
        try:
            r = ua_block_check(base + "/", lambda ua: fetch(base + "/", ua=ua))
        finally:
            stop()
        self.assertEqual(r["OAI-SearchBot"]["status"], "suspect")

    def test_200_challenge_title_is_blocked(self):
        def home(headers):
            if "Mozilla/5.0 (Windows" in headers.get("User-Agent", ""):
                return 200, HTML, self.NORMAL
            return 200, HTML, b"<html><head><title>Just a moment...</title></head></html>"
        base, stop = serve({"/": home})
        try:
            r = ua_block_check(base + "/", lambda ua: fetch(base + "/", ua=ua))
        finally:
            stop()
        self.assertEqual(r["PerplexityBot"]["status"], "suspect")


class RunTests(unittest.TestCase):
    def test_robots_octet_stream(self):
        base, stop = serve({"/": (200, HTML, b"<html><body>hi</body></html>"),
                            "/robots.txt": (200, {"Content-Type": "application/octet-stream"},
                                            b"User-agent: GPTBot\nDisallow: /\n")})
        try:
            r = run(base + "/", None, 5)
        finally:
            stop()
        self.assertEqual(r["ai_crawlers"]["GPTBot"]["status"], "warn")
        self.assertEqual(r["ai_crawlers"]["OAI-SearchBot"]["status"], "pass")

    def test_robots_503_unknown(self):
        base, stop = serve({"/": (200, HTML, b"<html><body>hi</body></html>"),
                            "/robots.txt": (503, TXT, b"down")})
        try:
            r = run(base + "/", None, 5)
        finally:
            stop()
        self.assertEqual(r["ai_crawlers"]["OAI-SearchBot"]["status"], "unknown")

    def test_homepage_challenge_is_unknown_not_down(self):
        challenge = (403, dict(HTML, **{"cf-mitigated": "challenge"}), b"<html><title>Just a moment...</title></html>")
        base, stop = serve({"/": challenge, "/robots.txt": (200, TXT, b"User-agent: *\nAllow: /\n")})
        try:
            r = run(base + "/", None, 5)
        finally:
            stop()
        self.assertEqual(r["homepage"]["status"], "unknown")
        self.assertEqual(r["ua_blocking"]["OAI-SearchBot"]["status"], "warn")

    def test_meta_robots_max_image_preview_none(self):
        page = b'<html><head><meta name="robots" content="index, follow, max-image-preview:none"></head></html>'
        base, stop = serve({"/": (200, HTML, page), "/robots.txt": (200, TXT, b"User-agent: *\nAllow: /\n")})
        try:
            r = run(base + "/", None, 5)
        finally:
            stop()
        self.assertEqual(r["meta_robots"]["status"], "pass")

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
