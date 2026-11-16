# AI 爬虫名单

更新日期：2026-11-16。本表与 `scripts/crawl_check.py` 中的 `AI_CRAWLERS` 常量同步维护，改一处须改另一处（`tests/test_references.py` 会检查）。

## 用途怎么判

- **训练**：采集数据训练模型。拦截它可以接受，不影响 AI 搜索的实时引用；但长期可能影响模型对品牌的"先验认知"（E12）。报告中记为 warn，不列 P0。
- **搜索检索**：为 AI 搜索建立索引。拦截等于让该 AI 搜索看不到本站，记为 fail，属于 P0（E2）。
- **用户触发**：用户在对话中提问或贴链接时实时抓取。拦截同样严重，属于 P0。

## 名单

| 名称 | robots.txt 标记 | 所属 | 市场 | 用途 | 说明 |
|---|---|---|---|---|---|
| GPTBot | `GPTBot` | OpenAI | 海外 | 训练 |  |
| OAI-SearchBot | `OAI-SearchBot` | OpenAI (ChatGPT 搜索) | 海外 | 搜索检索 |  |
| ChatGPT-User | `ChatGPT-User` | OpenAI | 海外 | 用户触发 |  |
| ClaudeBot | `ClaudeBot` | Anthropic | 海外 | 训练 |  |
| Claude-SearchBot | `Claude-SearchBot` | Anthropic | 海外 | 搜索检索 |  |
| Claude-User | `Claude-User` | Anthropic | 海外 | 用户触发 |  |
| PerplexityBot | `PerplexityBot` | Perplexity | 海外 | 搜索检索 |  |
| Perplexity-User | `Perplexity-User` | Perplexity | 海外 | 用户触发 |  |
| Google-Extended | `Google-Extended` | Google (Gemini 训练) | 海外 | 训练 | 仅 robots.txt 控制标记，无独立抓取 UA |
| Googlebot | `Googlebot` | Google (搜索 / AI Overview) | 海外 | 搜索检索 |  |
| Bingbot | `Bingbot` | Microsoft (Bing / Copilot，亦供 ChatGPT 部分检索) | 海外 | 搜索检索 |  |
| Applebot-Extended | `Applebot-Extended` | Apple (Apple Intelligence 训练) | 海外 | 训练 | 仅 robots.txt 控制标记，无独立抓取 UA |
| Meta-ExternalAgent | `Meta-ExternalAgent` | Meta | 海外 | 训练 |  |
| CCBot | `CCBot` | Common Crawl | 海外 | 训练 |  |
| Amazonbot | `Amazonbot` | Amazon (Alexa / Rufus) | 海外 | 搜索检索 |  |
| DuckAssistBot | `DuckAssistBot` | DuckDuckGo | 海外 | 搜索检索 |  |
| Bytespider | `Bytespider` | 字节跳动 (豆包) | 国内 | 训练 |  |
| Baiduspider | `Baiduspider` | 百度 (搜索 / 文心) | 国内 | 搜索检索 |  |
| Sogou web spider | `Sogou web spider` | 搜狗 (腾讯) | 国内 | 搜索检索 |  |
| YisouSpider | `YisouSpider` | 神马 / 夸克 (阿里) | 国内 | 搜索检索 |  |
| 360Spider | `360Spider` | 360 搜索 | 国内 | 搜索检索 |  |
| PetalBot | `PetalBot` | 华为 (花瓣搜索 / 小艺) | 国内 | 搜索检索 |  |
| Yeti | `Yeti` | Naver (搜索 / AI Briefing) | 韩国 | 搜索检索 |  |
| Daum | `Daum` | Daum (原 Kakao 运营的搜索) | 韩国 | 搜索检索 |  |

## 没有公开 UA 的国内引擎

- **腾讯元宝**：未公开独立爬虫 UA，联网检索依赖搜狗、微信搜一搜等合作方，因此 `Sogou web spider` 的放行很重要。
- **DeepSeek**：未公开爬虫 UA，联网搜索依赖第三方搜索服务。
- **Kimi（月之暗面）**：未公开爬虫 UA，依赖其搜索合作方。
- **豆包**：Bytespider 主要用于训练采集；豆包联网搜索还依赖字节自有搜索（头条搜索），同样受 Bytespider 放行情况影响。

这几家的可见度只能通过"能否被其搜索合作方收录"来间接判断，报告中标注"推断，证据较弱"。

## 关于伪装 UA 检测的局限

`crawl_check.py` 是在审计机上冒用这些 UA 发请求的。Cloudflare 等 CDN 会按 IP 验证真实爬虫，因此：伪装请求被拦，不代表真实爬虫被拦；伪装请求通过，也不代表真实爬虫能通过。结果为 `suspect` 时请客户核对 CDN/WAF 的 AI bot 设置（例如 Cloudflare 的 "Block AI bots" 或 "AI Crawl Control"）或查看服务器日志中真实爬虫的状态码。
