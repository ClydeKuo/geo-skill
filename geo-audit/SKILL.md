---
name: geo-audit
description: Use when a client wants their website to show up, be cited, or be recommended in AI answers (ChatGPT, Perplexity, Google AI Overviews, Gemini, Claude, Copilot, 豆包, DeepSeek, Kimi, 元宝, Naver AI Briefing, Le Chat), when asked for a GEO / 生成式引擎优化 / AI 検索最適化 / AI SEO / AEO audit of a site given only its URL without source code, for one or more countries or languages, or when re-checking a site after a previous GEO report.
---

# GEO 网站审计

## 概述

只凭一个网址，从外部排查网站在一个或多个国家 / 语言市场的 AI 搜索可见度，输出客户可以照着改的报告。

**核心原则**：按证据强度分配精力。最大的杠杆依次是**能被抓取 → 能被检索 → 能被吸收 → 站外有人提及**，而不是改写文案的套路。每条建议都必须引用 `references/evidence.md` 的证据编号和强度。

本 skill 遵循开放的 Agent Skills 格式，可在 Claude Code、Codex、Cursor 等工具中使用，用 `bash <skill>/install.sh` 安装到各工具的 skill 目录。下文所有路径都相对于**本 SKILL.md 所在的目录**（记为 `<skill>`）。

## 何时不用

- 传统 SEO 全量审计（外链、关键词排名）：只在与 GEO 相关时提及。
- 调用 AI 接口实测可见度：不做，报告中只给手动方法。
- 直接修改客户网站：只出报告，最多附 1–2 段示范改写。

## 需要的环境能力

| 能力 | 用途 | 没有时怎么办 |
|---|---|---|
| shell + Python 3 | 运行 `<skill>/scripts/` 下的检测脚本（只用标准库） | 无法审计，告知用户 |
| 网络访问 | 脚本抓取客户网站 | 第 1 步的试跑会发现，停止并提示用户开启联网 |
| 网页搜索工具（Claude Code 中为 WebSearch） | 站外提及 | 站外一节写"未能检测（当前环境无网页搜索）"，不得省略该节 |
| 网页抓取工具（Claude Code 中为 WebFetch） | 读站外页面 | 用 `curl` 代替 |
| 文件写入工具 | 写报告 | 用 shell heredoc |
| Chrome / Chromium（可选） | 渲染对比 | 脚本自动标"未检测" |

## 文件

| 文件 | 用途 |
|---|---|
| `scripts/crawl_check.py` | robots.txt 对 AI 爬虫的放行（RFC 9309）、UA 拦截对照、sitemap、canonical、noindex、HTTPS、llms.txt、ICP、hreflang（HTML / HTTP Link 头 / sitemap 三来源及双向检查） |
| `scripts/render_diff.py` | 不执行 JS 时与渲染后的正文比例 |
| `scripts/page_audit.py` | 标题层级、证据单元、结构化数据、作者与更新时间、canonical、hreflang；`--save-html` 保存原始 HTML |
| `references/checklist.md` | 通用检查清单与 P0/P1/P2 规则 |
| `references/markets/<代码>.md` | 市场档案：`cn` `us` `jp` `kr` `de` `fr` `es`；未建档市场用 `_generic.md` |
| `references/evidence.md` | 证据库 E1–E16 |
| `references/ai-crawlers.md` | 爬虫用途、无公开 UA 的引擎、伪装 UA 的局限 |
| `references/report-template.md` | 报告结构与写作规则（必须使用） |

所有脚本的通用参数：`python3 <skill>/scripts/<脚本>.py <url> [更多 url…] [--proxy URL] [--timeout 秒] [--lang 语言标签] [--out 文件.json]`，结果以 JSON 输出到标准输出，任何情况下退出码都是 0。`crawl_check.py` 只接受一个 url，另有 `--markets cn,us,jp`。

## 审计流程

先建立输出目录 `geo-report-<主机名>-<YYYYMMDD>/`（放在当前工作目录下；`<主机名>` 取首页最终地址的主机名原样，如 `www.example.com`），所有原始数据都存到这里。报告文件 `geo-report-<主机名>-<YYYYMMDD>.md` 与它放在同一级。

1. **收集上下文**
   - 网址必填。品牌、主营业务缺失时询问一次，用户不答就从首页推断，并写入报告的"审计范围与假设"。
   - **报告语言** = 用户发起审计时所用的语言；用户另行指定时以指定为准。
   - **目标市场**（市场代码列表）：用户点名的优先。没说时，先跑第 2 步，再从 `crawl.json` 的 `hreflang` 和语言切换器推断，请用户确认一次。一次审计**默认最多 3 个市场**；无人回答时取"网站默认语言对应的市场 + hreflang 中已建档的市场里最多 2 个（按 cn、us、jp、kr、de、fr、es 的顺序）"，其余列为"本次未审计的市场"。用户明确要求更多时照做，但页数和时间预算不变。
   - 市场按**国家或地区**划分。`zh-TW` / `zh-HK`、`en-GB` 等非美国英语、`de-AT` / `de-CH`、`fr-BE` / `fr-CA` 等都走 `_generic`，参考关系见 `markets/_generic.md` 第 1 节。
   - 确认审计机的网络出口国家（例如 `curl -s https://ipinfo.io/country`）。

2. **可抓取检查**（同时是联网试跑）
   ```bash
   python3 <skill>/scripts/crawl_check.py <url> --markets <代码列表> --out <输出目录>/crawl.json
   ```
   - 如果 `homepage` 和 `robots` 都是网络错误，说明当前环境不能联网：停止，告诉用户需要开启联网（Codex 的开启方式见 README），不要出空报告。
   - 读 `ai_crawlers`（`relevant` 为 true 的重点看）、`ua_blocking`、`homepage`、`robots.value.source`、`meta_robots`、`x_robots_tag`、`canonical`、`https`、`sitemap`、`icp`、`hreflang`、`other_domains`。判定规则见 `references/checklist.md`，本地爬虫见各市场档案第 4 节。
   - `sitemap.value.truncated` 为 true 时，`count` 只是已读取的数量，不是全站总数。
   - **其他主机上的语言版本**：`hreflang.declared` 中位于其他域名 / 子域名、且属于已选目标市场的版本，纳入本次审计，对其首页再跑一次 `crawl_check.py`，输出为 `crawl-<主机名>.json`。没有在 hreflang 中声明的其他域名（`other_domains`）只在报告中提示，建议另行审计。

3. **选重点页**：每个目标市场至少 2 页（该市场的语言版本），总数不超过 20。优先：首页、核心产品 / 服务页、对比页、定价页、关于页、内容页。来源优先用 sitemap 和导航。

4. **渲染对比**：每次传 1–5 个 URL，超时 30 秒，用对应市场的语言：
   ```bash
   python3 <skill>/scripts/render_diff.py <url1> <url2> --timeout 30 --lang ja-JP --out <输出目录>/render-1.json
   ```

5. **单页审计并阅读正文**：
   ```bash
   python3 <skill>/scripts/page_audit.py <url1> <url2> … --lang ja-JP --save-html <输出目录>/html --out <输出目录>/pages-jp.json
   ```
   - 脚本只负责计数，并排除 `<nav>` 和页面级 `<header>`、`<footer>` 中的链接与标题。
   - **阅读正文时读 `--save-html` 保存的文件**，不要另写抓取脚本，也不要把中间文件放到输出目录以外。
   - 要判断的内容：有没有定义句、对比、步骤、可核实的数据，是否一段只讲一个主张；隐藏正文（折叠的 FAQ 只在 JS 数据里、数字动画在 HTML 中显示为 0）；当地语言版本是否为人工本地化、是否有机翻痕迹；市场档案第 7 节的本地化要点。

6. **可检索判断**：每个目标市场用当地语言推演 10–20 个问题，句式参考市场档案第 6 节，覆盖认知 / 对比 / 决策 / 售后。逐条判断该市场语言版本中是否有页面直接回答，填入报告的"问题覆盖表"（当地语言原文 + 报告语言译文）。

7. **站外提及**：用网页搜索工具，按市场档案第 5 节的平台逐一查找，记录有 / 无 / 未能检测与代表链接。需要登录的平台不查。

8. **保存审计选择**：写入 `<输出目录>/audit.json`：
   ```json
   {"target": "", "markets": ["jp", "us"], "report_language": "ja", "brand": "", "business": "",
    "pages": {"jp": ["…"], "us": ["…"]}, "questions": {"jp": ["…"], "us": ["…"]},
    "offsite_queries": {"jp": ["…"], "us": ["…"]}, "extra_hosts": ["…"],
    "proxy_country": {"jp": "JP"}, "date": "YYYY-MM-DD"}
   ```
   `proxy_country` 只记录用过哪个国家的出口（没用过写 `{}`），不记录代理地址。

9. **写报告**：按 `references/report-template.md` 的结构，用报告语言书写。章节编号固定，不适用的写"不适用"。

### 复查模式

用户提供上一次的 `geo-report-<主机名>-<日期>/` 目录时：读取其中的 `audit.json`，**沿用同样的市场、重点页、推演问题和站外查询词**，重新执行第 2–7 步，填写报告的"整改前后对比"章节。

旧版 `audit.json` 使用 `"market": "cn" | "global" | "both"`，按以下规则换算：`"cn"` → `cn`；`"global"` → `us`；`"both"` → `cn,us`。旧版的 `questions` 键 `global` 对应 `us`。

## 限流与时间预算

- 脚本已内置退避：遇到 429 或带 Retry-After 的 503 会等待后重试一次，并自动放慢后续请求。结果中出现 `rate_limited: true`，或多个页面连续返回 429 时：
  - 把剩余重点页减到每个市场 2 页；
  - 在报告"审计范围与假设"中写明"站点限流，抽查页数已减少"。
- 整次审计建议在 **45 分钟**内完成。超过时停止新增抓取，用已有数据写报告，并注明未完成的检查。
- **禁止**为规避限流轮换代理或出口 IP，也不要改 UA、加速重试。
- 只有两种情况可以用 `--proxy` 指定某个国家的出口：测试该目标国家的可达性；站点按访问地区返回不同内容。用了哪个国家的出口要写进报告，**只写国家，不写代理地址**（代理地址属于审计方的内部信息，报告和 `audit.json` 都要交给客户）。

## 判读要点

| 脚本结果 | 含义 | 报告怎么写 |
|---|---|---|
| `ai_crawlers` 中检索类或用户触发类为 `fail` | robots.txt 明确拦截 | P0 |
| `ai_crawlers` 中为 `unknown` | robots.txt 读不到 | 写"未能检测"及原因 |
| `ai_crawlers` 中训练类为 `warn` | 拦截了训练爬虫 | 只说明利弊 |
| `ua_blocking` 为 `suspect` | 浏览器 UA 正常，伪装的 AI UA 被拦 | P1，"疑似"，请客户核对 CDN/WAF 或服务器日志 |
| `ua_blocking` 为 `warn` / `unknown` | 都被拦 / 被限流或请求失败 | 说明审计受限 |
| `homepage` 为 `unknown` | 审计机被 WAF 挑战 | 不是"网站不可用"，需从其他网络核实 |
| `render_diff` 的 `ratio` < 0.5 | AI 爬虫基本看不到正文 | P0，列出 `js_only_headings` |
| `hreflang.alternates` 中 `fail` / `warn` | 语言版本打不开 / 不双向 | P1 / P2 |
| 任意项为 `unknown` | 没能检测 | 写"未能检测"及原因，**不评价** |
| `llms_txt` | 只记录有无 | 放进"不建议投入" |
| `raw_words` / `rendered_words` | 中日韩文字每字计 1，其他语言按单词计 | 不同语言的字数不能直接比较 |

## 红线

- 每条问题都要有证据，每条建议都要标证据编号和强度。目标市场不是 `us` 时加"（推断）"，除非市场档案第 8 节另有说明。未建档市场注明"该市场未建档，证据较弱"。
- 没抓到的内容写"未能检测"，不能凭印象评价。
- 不建议编造数据、伪造评价、刷评、隐藏给 AI 的指令、贬低竞品，也不建议用机器翻译批量生成多语言版本（E13）。
- 不把 llms.txt、FAQ 化、Schema、权威语气当作核心建议（E10、E9、E7）。
- 不承诺流量或排名的提升（E15）。
- 报告语言必须与用户提问的语言一致（用户另行指定时除外）。

## 常见错误

- **把 `suspect` 当成确定的拦截**：只有 robots.txt 的明确拦截才是 P0。
- **用 Google 排名推断 AI 可见度**：两者重叠很低（E13），各市场、各引擎要分开看。
- **用报告语言推演问题**：推演问题要用目标市场的当地语言和当地用户的问法。
- **只看脚本计数就下结论**：`numbers` 多不代表数据可核实，`external_links` 也可能混入用 `<div>` 写的页脚链接，要看正文。
- **把 sitemap 的 `count` 当成全站页面数**：`truncated` 为 true 时要注明。
- **被限流后硬撑**：按"限流与时间预算"一节减少页数，不要自写循环长时间等待。
- **漏掉其他主机上的语言版本**：`hreflang` 中声明在其他域名的目标市场版本要纳入审计。
