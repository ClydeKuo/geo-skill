# 海外市场检查清单

目标引擎：ChatGPT（搜索）、Perplexity、Google AI Overview / AI Mode / Gemini、Claude、Microsoft Copilot。
每一项都标注了对应的证据编号（见 `evidence.md`）。判定栏中的 P0/P1/P2 规则统一如下：

- **P0 阻断**：检索类 AI 爬虫被 robots.txt 明确拦截；核心页面不执行 JS 时正文比例 < 50%；首页不是 200；海外市场下从审计机访问不了。
- **P1 高**：核心问题没有页面直接回答；重点页面缺少可核实的证据单元；站外几乎没有第三方提及；伪装 AI UA 被 WAF 拦截（`suspect`，需要客户核对）。
- **P2 中**：标题层级混乱、缺更新时间或作者、description 与意图不符、结构化数据缺失（注明"证据弱，作为卫生项"）。

## 第1层 可抓取（脚本：`crawl_check.py`、`render_diff.py`）

- [ ] 首页状态码与响应时间（`homepage`）：非 200 → P0；> 3 秒 → P2。依据 E2。
- [ ] robots.txt 对海外检索类与用户触发类爬虫的放行（`ai_crawlers` 中 market=global、purpose=search/user）：任何一个被拦 → P0。依据 E2。
- [ ] robots.txt 对海外训练类爬虫（GPTBot、ClaudeBot、Google-Extended、Applebot-Extended、CCBot、Meta-ExternalAgent）：被拦 → 只记录，说明利弊，由客户决定。依据 E12。
- [ ] WAF / CDN 是否拦截 AI UA（`ua_blocking`）：`suspect` → P1，请客户核对 CDN 设置；`warn`（连浏览器 UA 也被拦）→ 在报告中说明审计受限。依据 E2、E11。
- [ ] 不执行 JS 时的正文比例（`render_diff.py` 的 `ratio`）：< 0.5 → P0；0.5–0.8 → P1；列出只在渲染后才出现的标题。依据 E11。
- [ ] meta robots / X-Robots-Tag 是否含 noindex：重点页含 noindex → P0。依据 E2。
- [ ] sitemap 是否存在、是否覆盖重点页：缺失 → P2。依据 E2。
- [ ] canonical 是否指向自身：指向其他 URL 且非有意 → P1。依据 E2。
- [ ] HTTPS：否 → P2。依据 E2。
- [ ] llms.txt：只记录有无，不作为建议。依据 E10。

## 第2层 可检索（agent 判断）

- [ ] 推演 10–20 个英文用户问题，覆盖认知 / 对比 / 决策 / 售后四个阶段，包括"best X for Y""X vs Y""how to …""is X worth it"等句式。依据 E1、E15。
- [ ] 每个问题：站内是否有页面的 title 或 H2/H3 直接对应，是否有一段话直接给出答案。核心问题无覆盖 → P1。依据 E1。
- [ ] 页面 title 与 meta description 是否用用户的问法，而不是内部口号。依据 E1。
- [ ] 是否有对比页、价格页、规格页、售后/故障排查页（AI 回答商业问题时常用）。依据 E1、E4、E12。
- [ ] 英文内容是否真正面向海外用户（不是机翻、单位和货币本地化）。依据 E13。

## 第3层 可吸收（脚本：`page_audit.py` + agent 阅读正文）

- [ ] 重点页是否包含可核实的数据（`numbers`）、日期（`dates`）、外部引用（`external_links`）、引语（`blockquotes`）：几乎为零 → P1。依据 E3、E16。
- [ ] 是否有明确的定义句、对比表（`tables`）、操作步骤（有序列表）。依据 E3。
- [ ] 价格、规格、更新日期是否为页面上的明文。依据 E4。
- [ ] 标题层级：H1 恰好 1 个、无跳级（`h1_count`、`heading_skips`）；不符合 → P2。依据 E5。
- [ ] 是否一段只讲一个主张、每段可以单独被引用（agent 判断）。依据 E3、E5。
- [ ] 作者与更新时间（`author`、`date_modified`）：缺失 → P2（卫生项）。依据 E9。
- [ ] 结构化数据（`jsonld_types`）：缺 Organization / Product / Article 等 → P2（卫生项，证据弱）。依据 E9。
- [ ] 有没有关键词堆砌、空洞的权威腔调：有 → 建议删改。依据 E7、E8。

## 第4层 站外提及（agent 用 WebSearch / WebFetch）

- [ ] Wikipedia 是否有品牌或产品词条，或在相关词条中被提及。依据 E12。
- [ ] Reddit、行业论坛中是否有真实讨论。依据 E12。
- [ ] 行业媒体报道、专业评测。依据 E12。
- [ ] "best X" 类榜单 / 对比文章中是否出现。依据 E12。
- [ ] G2、Capterra、Trustpilot、Amazon 等评价平台（视行业）。依据 E12。
- [ ] 几乎没有第三方提及 → P1，给出可执行的 PR / 评测 / 榜单策略（不得建议伪造评价）。依据 E12。
