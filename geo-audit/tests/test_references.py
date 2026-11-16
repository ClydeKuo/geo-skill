import os
import re
import unittest

from helpers import HERE

from crawl_check import AI_CRAWLERS

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

    def test_checklists_cite_evidence(self):
        for name in ("checklist-global.md", "checklist-cn.md"):
            for line in read(name).splitlines():
                if line.lstrip().startswith("- [ ]"):
                    self.assertRegex(line, r"E\d+", "%s: %s" % (name, line))

    def test_template_sections(self):
        doc = read("report-template.md")
        for s in ("摘要", "审计范围与假设", "问题覆盖表", "示范改写", "站外提及", "不建议投入",
                  "实测可见度", "整改前后对比", "附录"):
            self.assertIn(s, doc)


if __name__ == "__main__":
    unittest.main()
