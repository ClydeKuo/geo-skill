# 美国 / 英语市场档案

## 1. 基本信息

- 市场代码：us
- 语言标签：en-US
- 核对日期：2026-11-16
- 适用范围：美国。英国、澳大利亚、加拿大、印度等其他英语地区走 `_generic`，可参考本档案的引擎与平台，但这些地区的用户习惯、搜索份额和站外平台未经本档案核实，证据仍属推断。

## 2. 主流 AI 助手与 AI 搜索

按 Pew 2026 年 2 月调查中美国成年人"曾使用"比例排序（49% 的美国成年人使用 AI 聊天机器人，24% 每天使用；"查找信息"是最常见用途，占 42%）[S1][S2]：

| 产品 | 运营方 | 美国成年人使用比例 | 是否联网检索 | 依赖的搜索索引（已知时） |
|---|---|---|---|---|
| ChatGPT（含 ChatGPT search） | OpenAI | 44% [S1] | 是 | 第三方搜索提供商 + 合作伙伴内容 [S5]；TechCrunch 报道 OpenAI 与 Bing 合作，同时使用未公开的其他来源 [S6] |
| Gemini | Google | 24% [S1] | 是 | Google 搜索（Grounding with Google Search）[S7] |
| Microsoft Copilot | Microsoft | 17% [S1] | 是 | Bing 搜索服务 [S8] |
| Meta AI | Meta | 14% [S1] | 是（可获取网络实时信息）[S12] | 官方未公开搜索提供方，本档案不作推断 |
| Grok | xAI | 8% [S1] | — | 未核实，不作推断 |
| Claude | Anthropic | 6% [S1] | 是 | 据 TechCrunch，Anthropic 的子处理方名单列有 Brave Search，引用结果与 Brave 一致；Anthropic 未正式确认 [S6] |
| Perplexity | Perplexity AI | Pew 2026 未单列 | 是 | 自建索引（PerplexityBot 抓取），并与未具名的第三方爬虫合作 [S9][S10] |

搜索引擎内嵌的 AI：
- Google AI Overviews：60% 的美国成年人表示会阅读搜索结果顶部的 AI 摘要 [S1]。
- Google AI Mode：2025-05-20 起向全美用户开放 [S3]。

## 3. 搜索引擎与 AI 的关系

- 份额（Statcounter，2026 年 10 月，全平台，美国）：Google 85.45%、Bing 9.78%、Yahoo! 2.54%、DuckDuckGo 1.74% [S4]。Statcounter 统计的是带其追踪代码网站的引荐流量，不等于搜索次数。
- Google 索引 → AI Overviews、AI Mode、Gemini [S3][S7]。在 Google 有排名不等于在这些 AI 功能里被引用（见 evidence.md E13）。
- Bing 索引 → Microsoft Copilot [S8]；ChatGPT search 也部分依赖 Bing [S5][S6]。Bing 在美国的份额虽然远低于 Google，但它影响 ChatGPT 和 Copilot 两个大流量助手，审计时应确认站点已被 Bing 收录（可用 Bing Webmaster Tools）。
- OpenAI 自有抓取（OAI-SearchBot）、Perplexity 自建索引（PerplexityBot）[S9][S10]、Claude 疑似使用 Brave 索引 [S6]：这些不依赖 Google 排名，需要分别确认爬虫放行。
- 内容授权：Google（2024-02）、OpenAI（2024-05）都与 Reddit 签了 Data API 合作，可获取 Reddit 实时结构化内容 [S11][S13]，这能部分解释 Reddit 在美国 AI 回答中引用量高的现象（因果未经证实）。

## 4. 本地爬虫

无，主要依赖全球通用爬虫。

## 5. 站外重点平台

Peec AI 2026-03 统计了美国市场 ChatGPT、Google AI Mode、Gemini、Perplexity、AI Overviews 的 3,000 万条引用来源 [S14]：

- 总体被引用最多的前 10 个域名：Reddit、YouTube、LinkedIn、Wikipedia、Forbes、G2、Yelp、Facebook、Medium、TechRadar。Trustpilot、Tripadvisor、Clutch 进入前 100。
- 不同引擎偏好不同：
  - ChatGPT：Wikipedia、Reddit、Forbes、TechRadar、LinkedIn（偏编辑类媒体）
  - Perplexity：Reddit、YouTube、LinkedIn、Wikipedia、G2
  - Gemini：Reddit、YouTube、Wikipedia、Medium、PCMag/Forbes
  - AI Mode：YouTube、Reddit、Facebook、LinkedIn、Yelp（Yelp 在本地类问题中较突出）
  - AI Overviews：YouTube、Reddit、Facebook、LinkedIn、Medium
  - Wikipedia 没有进入两个 Google 产品的前 5。

按平台类型的检查重点：
- 百科：Wikipedia（品牌词条或在品类词条中被提及）。
- 问答社区：Reddit（相关 subreddit 中的真实讨论）。
- 视频平台：YouTube（测评、教程、开箱）。
- 职业社交：LinkedIn（B2B 品牌、公司页面、高管文章）。
- 评测媒体与 "best X" 榜单：Forbes、TechRadar、PCMag 等行业媒体的评测和 "best X for Y" 文章。
- 点评 / 评价平台：G2（B2B 软件，Perplexity 中尤其突出）、Yelp（本地商家）、Trustpilot、Clutch（服务商）。Capterra 在上述研究中未出现，按行业视情况检查。
- 需要登录才能完整查看的平台：Facebook、LinkedIn 的部分内容需登录，审计时可能看不全，应在报告中注明。

注意：不同研究的统计口径（全部引用占比 / 前 10 占比 / 提及占比）不同，排名差异很大；上述名单只说明"哪些平台值得检查"，不说明具体权重。

## 6. 用户提问方式

- 认知：What is the best `<品类>` for `<场景>`?（适合 `<场景>` 的最好的 `<品类>` 是什么？）
- 认知：How does `<品类>` work, and do I need one?（`<品类>` 是怎么工作的，我需要吗？）
- 对比：`<品牌>` vs `<竞品>`: which one should I buy?（`<品牌>` 和 `<竞品>` 比，该买哪个？）
- 对比：What are the best alternatives to `<品牌>`?（`<品牌>` 有哪些更好的替代品？）
- 决策：Is `<品牌>` `<型号>` worth it in 2026?（2026 年 `<品牌>` `<型号>` 值得买吗？）
- 决策：How much does `<品类>` cost, and where can I buy it in the US?（`<品类>` 要多少钱，在美国哪里能买到？）
- 决策：Is `<品牌>` legit? What do Reddit users say about it?（`<品牌>` 靠谱吗？Reddit 上的用户怎么说？）
- 售后：How do I fix `<型号>` `<故障现象>`?（`<型号>` 出现 `<故障现象>` 怎么修？）
- 售后：What is `<品牌>`'s return policy and warranty?（`<品牌>` 的退货政策和保修是什么？）

## 7. 本地化检查要点

- 货币与价格：en-US 的货币格式为 `$1,234.56`（千位逗号、小数点）[S15]；检查价格是否为页面明文、是否标明 USD（多币种站点尤其需要）。
- 日期与数字：en-US 短日期为 M/d/yyyy（如 5/28/2012），长日期如 "Tuesday, June 30, 2009"，时间为 12 小时制带 AM/PM [S15]。检查页面上的更新日期是否会被误读（如 03/04 在美国读作 3 月 4 日）。
- 计量单位、电话与地址格式、销售税说明、配送与支付方式：本档案未找到可直接引用的权威来源，审计时按目标用户的实际习惯核对，不在报告中作为有据结论。
- 隐私（加州 CCPA）：满足门槛（年总收入超过 2,500 万美元，或买卖 / 共享 10 万以上加州居民或家庭的个人信息，或一半以上收入来自出售加州居民个人信息）的营利性企业，须提供隐私政策、收集时告知；若出售或共享个人信息，须在网站上提供醒目的 "Do Not Sell or Share My Personal Information" 链接 [S16]。审计时只记录有无，合规判断交给客户法务。
- 评价合规（FTC）：FTC 2024 年最终规则禁止虚假评价（含 AI 生成的、来自不存在的人的评价）、以特定倾向为条件的付费评价、未披露关系的内部人员评价、冒充独立评测站的自营网站、压制差评，以及买卖虚假粉丝 / 浏览量 [S17]。站外策略建议不得触碰这些行为（与 evidence.md 的伦理红线一致）。

## 8. 证据适用性

直接证据。evidence.md 中的研究大多基于英文 / 美国市场（ChatGPT、Perplexity、Google AI Overview、Gemini 等），对美国市场属于"直接证据"，可按各条目标注的强度直接引用。站外平台部分另有美国本地数据可参考（Peec AI 美国市场 3,000 万条引用 [S14]），但它是观察性行业研究，强度不高于 E12。其他英语地区（英国、澳大利亚、加拿大、印度等）走 `_generic`，引用时仍写"推断，证据较弱"。

## 9. 来源

- [S1] Pew Research Center, "How opinions and use of AI differ by age"（Americans and AI 2026 报告章节，2026-06-17）https://www.pewresearch.org/internet/2026/06/17/how-opinions-and-use-of-ai-differ-by-age/ （访问 2026-11-16）
- [S2] Pew Research Center, "Americans and AI 2026: Chatbots, Smart Devices and Views on Impact"（2026-06-17）https://www.pewresearch.org/internet/2026/06/17/americans-and-ai-2026-chatbots-smart-devices-and-views-on-impact/ （访问 2026-11-16）
- [S3] Google, "AI in Search: Going beyond information to intelligence"（Google I/O 2025，2025-05-20）https://blog.google/products/search/google-search-ai-mode-update/ （访问 2026-11-16）
- [S4] Statcounter, "Search Engine Market Share United States Of America"（2026 年 10 月数据）https://gs.statcounter.com/search-engine-market-share/all/united-states-of-america （访问 2026-11-16）
- [S5] OpenAI, "Introducing ChatGPT search"（2024-10-31，原文称 ChatGPT search "leverages third-party search providers, as well as content provided directly by our partners"；本次访问被 Cloudflare 拦截，措辞经多个二手来源转述核对）https://openai.com/index/introducing-chatgpt-search/ （访问 2026-11-16）
- [S6] TechCrunch（Yahoo Finance 转载）, "Anthropic appears to be using Brave to power web search for its Claude chatbot"（2025-03-21）https://finance.yahoo.com/news/anthropic-appears-using-brave-power-170703042.html （访问 2026-11-16）
- [S7] Google AI Studio 文档, "Grounding with Google Search" https://aistudio.google.com/docs/google-search （访问 2026-11-16）
- [S8] Microsoft Learn, "Data, privacy, and security for web search in Microsoft Copilot and Microsoft Copilot Chat"（更新于 2026-11-04）https://learn.microsoft.com/en-us/microsoft-365/copilot/manage-public-web-access （访问 2026-11-16）
- [S9] Perplexity 文档, "Perplexity Crawlers" https://docs.perplexity.ai/guides/bots （访问 2026-11-16）
- [S10] Perplexity Research, "Architecting and Evaluating an AI-First Search API"（2025-09-25）https://research.perplexity.ai/articles/architecting-and-evaluating-an-ai-first-search-api （访问 2026-11-16）
- [S11] Google, "An expanded partnership with Reddit"（2024-02-22）https://blog.google/inside-google/company-announcements/expanded-reddit-partnership/ （访问 2026-11-16）
- [S12] Meta, "Meet Your New Assistant: Meta AI, Built With Llama 3"（2024-04-18，2024-07-03 更新）https://about.fb.com/news/2024/04/meta-ai-assistant-built-with-llama-3/ （访问 2026-11-16）
- [S13] Silicon Republic, "OpenAI and Reddit team up to bring more data to ChatGPT"（2024-05）https://www.siliconrepublic.com/business/openai-reddit-partnership-chatgpt-ai-data （访问 2026-11-16）
- [S14] Peec AI, "Top domains cited by AI search: Analysis based on 30M sources"（2026-03-31）https://peec.ai/blog/top-domains-cited-by-ai-search-analysis-based-on-30m-sources （访问 2026-11-16）
- [S15] Microsoft Learn, "Overview: How to format numbers, dates, enums, and other types in .NET" https://learn.microsoft.com/en-us/dotnet/standard/base-types/formatting-types （访问 2026-11-16）
- [S16] California Department of Justice, "California Consumer Privacy Act (CCPA)" https://oag.ca.gov/privacy/ccpa （访问 2026-11-16）
- [S17] FTC, "Federal Trade Commission Announces Final Rule Banning Fake Reviews and Testimonials"（2024-08-14）https://www.ftc.gov/news-events/news/press-releases/2024/08/federal-trade-commission-announces-final-rule-banning-fake-reviews-testimonials （访问 2026-11-16）
