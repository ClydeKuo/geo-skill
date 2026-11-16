import os
import re
import unittest

from helpers import HERE

from crawl_check import AI_CRAWLERS, MARKETS

REF = os.path.join(os.path.dirname(HERE), "references")


def read(name):
    with open(os.path.join(REF, name), encoding="utf-8") as f:
        return f.read()


class ReferenceTests(unittest.TestCase):
    def test_crawler_doc_matches_constant(self):
        doc = read("ai-crawlers.md")
        for c in AI_CRAWLERS:
            self.assertIn(c["name"], doc)

    def test_evidence_ids(self):
        doc = read("evidence.md")
        sections = re.split(r"^## ", doc, flags=re.M)
        found = {}
        for sec in sections:
            m = re.match(r"(E\d+)\b", sec)
            if m:
                found[m.group(1)] = sec
        for i in range(1, 17):
            self.assertIn("E%d" % i, found)
            self.assertIn("http", found["E%d" % i], "E%d 缺少来源链接" % i)

    def test_checklist_cites_evidence(self):
        items = [ln for ln in read("checklist.md").splitlines() if ln.lstrip().startswith("- [ ]")]
        self.assertGreater(len(items), 20)
        for line in items:
            self.assertRegex(line, r"E\d+", line)
        for old in ("checklist-global.md", "checklist-cn.md"):
            self.assertFalse(os.path.exists(os.path.join(REF, old)), old)

    def test_template_sections(self):
        doc = read("report-template.md")
        for s in ("摘要", "审计范围与假设", "问题覆盖表", "示范改写", "站外提及", "不建议投入",
                  "实测可见度", "整改前后对比", "附录", "本次未审计的市场", "多语言"):
            self.assertIn(s, doc)


HEADINGS = ["## 1. 基本信息", "## 2. 主流 AI 助手与 AI 搜索", "## 3. 搜索引擎与 AI 的关系", "## 4. 本地爬虫",
            "## 5. 站外重点平台", "## 6. 用户提问方式", "## 7. 本地化检查要点", "## 8. 证据适用性", "## 9. 来源"]


def section(doc, n):
    start = doc.index(HEADINGS[n - 1])
    end = doc.index(HEADINGS[n]) if n < len(HEADINGS) else len(doc)
    return doc[start:end]


class MarketProfileTests(unittest.TestCase):
    def profiles(self):
        return ["_generic"] + list(MARKETS)

    def test_market_profiles_structure(self):
        for code in self.profiles() + ["_template"]:
            doc = read(os.path.join("markets", code + ".md"))
            for h in HEADINGS:
                self.assertIn(h, doc, "%s 缺少 %s" % (code, h))
            if code == "_template":
                continue
            self.assertIn("核对日期：", section(doc, 1), code)
            self.assertIn("市场代码：", section(doc, 1), code)
            self.assertIn("语言标签：", section(doc, 1), code)
            if code != "_generic":
                self.assertGreaterEqual(section(doc, 9).count("http"), 2, code)

    def test_market_crawlers_exist(self):
        names = {c["name"] for c in AI_CRAWLERS}
        for code in self.profiles():
            sec = section(read(os.path.join("markets", code + ".md")), 4)
            for name in re.findall(r"`([^`]+)`", sec):
                self.assertIn(name, names, "%s 第4节的爬虫 %s 不在 AI_CRAWLERS 中" % (code, name))


SKILL_MD = os.path.join(os.path.dirname(HERE), "SKILL.md")


class SkillDocTests(unittest.TestCase):
    def doc(self):
        with open(SKILL_MD, encoding="utf-8") as f:
            return f.read()

    def test_no_claude_specific_terms(self):
        doc = self.doc()
        self.assertNotIn("Base directory", doc)
        for line in doc.splitlines():
            if "WebSearch" in line or "WebFetch" in line:
                self.assertIn("Claude Code", line, line)

    def test_frontmatter(self):
        doc = self.doc()
        self.assertTrue(doc.startswith("---\n"))
        fm = doc.split("---\n")[1]
        keys = [ln.split(":", 1)[0] for ln in fm.splitlines() if ln and not ln.startswith(" ")]
        self.assertEqual(keys, ["name", "description"])
        self.assertIn("name: geo-audit", fm)
        self.assertLessEqual(len(fm), 1024)

    def test_mentions_new_flags(self):
        doc = self.doc()
        for s in ("--markets", "--lang", "--save-html", "install.sh", "rate_limited", "markets/", "checklist.md"):
            self.assertIn(s, doc, s)
        self.assertNotIn("checklist-cn", doc)
        self.assertNotIn("checklist-global", doc)

    def test_legacy_audit_json_mapping(self):
        doc = self.doc()
        self.assertIn('"both"', doc)
        self.assertIn("cn,us", doc)

    def test_proxy_address_not_in_report_rule(self):
        doc = self.doc()
        self.assertIn("不写代理地址", doc)
        self.assertIn('"proxy_country"', doc)

    def test_no_private_info(self):
        files = [SKILL_MD] + [os.path.join(dp, f) for dp, _, fs in os.walk(REF) for f in fs]
        for path in files:
            with open(path, encoding="utf-8") as f:
                self.assertNotIn("192.168.", f.read(), path)


if __name__ == "__main__":
    unittest.main()
