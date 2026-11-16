---
name: geo-audit
description: Use when a client wants their website to show up, be cited, or be recommended in AI answers (ChatGPT, Perplexity, Google AI Overview, Gemini, Claude, 豆包, DeepSeek, Kimi, 腾讯元宝, 文心), when asked for GEO / 生成式引擎优化 / AI 搜索可见度 / AI SEO / AEO audit of a site given only its URL without source code, or when re-checking a site after a previous GEO report.
---

# GEO 网站审计

## 概述

只凭一个网址，从外部排查网站在 AI 搜索中的可见度，输出一份客户可以照着改的中文报告。

**核心原则**：按证据强度分配精力。研究表明，最大的杠杆依次是**能被抓取 → 能被检索 → 能被吸收 → 站外有人提及**，而不是改写文案的套路。每条建议都必须引用 `references/evidence.md` 的证据编号和强度。

## 何时不用

- 客户要的是传统 SEO 全量审计（外链、关键词排名）：本 skill 只在与 GEO 相关时提及。
- 要调用 AI 接口实测可见度：本 skill 不做（报告中只给手动方法）。
- 要直接修改客户网站：本 skill 只出报告，最多附 1–2 段示范改写。

## 文件

`<skill 目录>` 指本 skill 所在目录（加载时显示的 Base directory）。脚本只依赖 Python 3 标准库；渲染对比需要系统中的 Chrome / Chromium（找不到时自动标"未检测"）。

| 文件 | 用途 |
|---|---|
| `scripts/crawl_check.py` | 第1层：robots.txt 对 22 个 AI 爬虫的放行、UA 拦截对照、sitemap、canonical、noindex、HTTPS、llms.txt、ICP、同品牌其他域名 |
| `scripts/render_diff.py` | 第1层：不执行 JS 时与渲染后的正文比例 |
| `scripts/page_audit.py` | 第2/3层：标题层级、证据单元（数据/日期/外链/引语/表格）、结构化数据、作者与更新时间 |
| `references/evidence.md` | 证据库 E1–E16，报告中引用的唯一依据 |
| `references/checklist-global.md` / `checklist-cn.md` | 海外 / 国内检查清单与 P0/P1/P2 判定规则 |
| `references/ai-crawlers.md` | 爬虫用途说明、无公开 UA 的国内引擎、伪装 UA 的局限 |
| `references/report-template.md` | 报告模板（必须使用） |

所有脚本的命令行参数相同：`python3 <skill 目录>/scripts/<脚本>.py <url> [更多 url…] [--proxy URL] [--timeout 秒] [--out 文件.json]`，结果以 JSON 输出到标准输出。`crawl_check.py` 只接受一个 url。

## 审计流程

先建立输出目录：`geo-report-<主机名>-<YYYYMMDD>/`（放在当前工作目录下），所有原始 JSON 都存到这里。`<主机名>` 取首页最终地址的主机名原样，例如 `www.example.com`。

**一次审计只审一个站点。** 如果另一个目标市场的站点在别的域名上（例如海外是 `brand.com`、国内是 `brand.cn`）：本次只审用户给的网址；在报告"审计范围与假设"和"站外提及"中写明发现的其他域名，并建议另做一次审计。用户明确要求两个都审时，分两次执行本流程，生成两个独立的输出目录和两份报告。查找其他域名的途径：`crawl.json` 的 `other_domains`，加上 WebSearch"<品牌> 官网"（脚本只能发现首页链接到的同名域名）。

1. **收集上下文**。网址必填。品牌名、主营业务、目标市场（国内 / 海外 / 两者）缺失时询问一次；用户不答就从首页推断，并在报告"审计范围与假设"中写明。确认审计机的网络出口（`curl -s https://myip.ipip.net`）：没有中国大陆出口时，国内可达性一项标"未检测（无大陆出口）"。

2. **可抓取检查**：
   ```bash
   python3 <skill 目录>/scripts/crawl_check.py <url> --out <输出目录>/crawl.json
   ```
   读 `ai_crawlers`、`ua_blocking`、`homepage`、`meta_robots`、`x_robots_tag`、`sitemap`、`other_domains`。判定规则见对应市场的清单。`sitemap.value.truncated` 为 true 时，`count` 只是已读取的数量，不是全站总数。

3. **选重点页**，每次审计最多 20 个：首页、核心产品 / 服务页、对比页、定价页、关于页、2–3 篇内容页。来源优先用 `crawl.json` 的 sitemap URL 和首页导航。两个市场共用一个站点时，两种语言的版本都要选。

4. **渲染对比**。每次传 1–5 个 URL，超时用 30 秒：
   ```bash
   python3 <skill 目录>/scripts/render_diff.py <url1> <url2> --timeout 30 --out <输出目录>/render-1.json
   ```

5. **单页审计**，然后**阅读正文**：
   ```bash
   python3 <skill 目录>/scripts/page_audit.py <url1> <url2> … --out <输出目录>/pages.json
   ```
   脚本只负责计数，并且计数会排除 `<nav>` 以及页面级 `<header>`、`<footer>` 里的链接和标题。注意检查每页的 `canonical`：指向别的地址或会跳转的地址，按 P1 处理。是否有定义句、对比、步骤、可核实的数据，是否一段只讲一个主张，要靠你阅读页面正文来判断（用 WebFetch，或者从脚本抓到的 HTML 里提取）。

6. **可检索判断**。每个目标市场推演 10–20 个用户会问 AI 的问题，覆盖认知 / 对比 / 决策 / 售后四个阶段。海外用英文，国内用中文口语。逐条判断站内是否有页面的标题或段落直接回答，填进"问题覆盖表"。

7. **站外提及**。用 WebSearch / WebFetch 按清单第4层的平台逐一查找，记录有 / 无 / 未能检测，并附代表链接。需要登录的平台不查，标"未能检测"。

8. **保存审计选择**，写入 `<输出目录>/audit.json`：
   ```json
   {"target": "", "market": "cn|global|both", "brand": "", "business": "",
    "pages": ["…"], "questions": {"cn": ["…"], "global": ["…"]},
    "offsite_queries": ["…"], "date": "YYYY-MM-DD"}
   ```

9. **写报告**。复制 `references/report-template.md` 的结构，保留全部章节编号（不适用的章节写"不适用"，不要删除），写到 `geo-report-<域名>-<YYYYMMDD>.md`，与输出目录放在同一级。只有一个目标市场时，删掉另一个市场的小节（3.1 或 3.2）。

### 复查模式

用户提供上一次的 `geo-report-<域名>-<日期>/` 目录时：读取其中的 `audit.json`，**沿用同样的重点页、推演问题和站外查询词**，重新执行第 2–7 步，然后填写报告的"整改前后对比"章节，逐项列出 pass / warn / fail / suspect 的变化。

## 判读要点

| 脚本结果 | 含义 | 报告怎么写 |
|---|---|---|
| `ai_crawlers` 中检索类或用户触发类为 `fail` | robots.txt 明确拦截了该爬虫 | P0 |
| `ai_crawlers` 中训练类为 `warn` | 拦截了训练爬虫 | 只说明利弊，不列为问题 |
| `ua_blocking` 为 `suspect` | 浏览器 UA 访问正常，伪装的 AI UA 被拦 | P1，"疑似"，请客户核对 CDN/WAF 设置或服务器日志 |
| `ua_blocking` 为 `warn` | 连浏览器 UA 也被拦 | 说明审计受限，需要人工复核 |
| `render_diff` 的 `ratio` < 0.5 | AI 爬虫基本看不到正文 | P0，列出 `js_only_headings` |
| 某项为 `unknown` | 脚本没能检测 | 写"未能检测"及原因，**不评价** |
| `llms_txt` | 只记录有无，有无都是 `pass` | 放进"不建议投入"一节 |
| `render_diff` 的 `raw_words` / `rendered_words` | 中日韩文字每字计 1，英文按单词计 | 中英文页面的字数不能直接比较 |

## 红线

- 报告里的每条问题都要有证据（数值、原文或 URL），每条建议都要标证据编号和强度。国内市场的建议加"（推断）"。
- 抓取失败或没读到的内容，写"未能检测"，不能凭印象评价。
- 不建议编造数据、伪造评价、刷评、隐藏给 AI 的指令或贬低竞品。需要客户补充的数据写【待客户提供】。
- 不把 llms.txt、FAQ 化、Schema、权威语气当作核心建议（分别见 E10、E9、E7）。
- 不承诺流量或排名的提升（E15）。
- 抓取要克制：串行请求，每次审计不超过 20 个重点页。

## 常见错误

- **把 `suspect` 当成确定的拦截**：脚本是从审计机伪装 UA，CDN 会按 IP 识别真实爬虫。只有 robots.txt 的明确拦截才是 P0。
- **用 Google 排名推断 AI 可见度**：两者重叠很低（E13），要分开看。
- **只看脚本计数就下结论**：`numbers` 多不代表数据可核实，还要读正文。
- **用自己的偏好推演问题**：推演的问题要用用户的口吻和问法（"X 哪个牌子好"、"best X for Y"），不要用客户的品牌口号。
- **把 sitemap 的 `count` 当成全站页面数**：`truncated` 为 true 时，要在报告里写"已读取 N 条，未读完"。
- **只看 `ratio` 判断"能不能看到"**：渲染对比只比较字数。有些内容渲染后仍然看不到，比如折叠的 FAQ 答案只存在于 JS 数据里，或者数字动画在 HTML 中显示为 0。阅读正文时要专门检查这两类情况，发现了就按第3层问题写。
- **相信 `external_links` 一定是"引用来源"**：有的站页脚是用 `<div>` 写的，社交、姊妹站链接仍会被计入。要看具体链接再下结论。
- **Write 工具被拒绝**（例如在子代理里运行）：改用 Bash 的 heredoc 写文件。
