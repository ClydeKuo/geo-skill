# 市场档案：法国（fr）

## 1. 基本信息

- 市场代码：fr
- 语言标签：fr-FR
- 核对日期：2026-11-16
- 适用范围：法国本土（法语）。比利时、瑞士、加拿大法语区走 `_generic`，可参考本档案：语言和部分法语媒体相通，但 Google AI 功能上线时间、搜索份额、法律页面、货币（瑞士 CHF、加拿大 CAD）和数字格式要按当地另行核实，本档案没有覆盖。

## 2. 主流 AI 助手与 AI 搜索

整体使用：CRÉDOC《Baromètre du numérique 2026》（为 Arcep、Arcom、CGE、ANCT 编制，2025 年 6 月调查 12 岁以上人群）显示 48% 的法国人使用生成式 AI [1]。在 AI 用户中，受访者可列出最常用的三个工具：

| 产品 | 运营方 | AI 用户中提到的比例 / 列为首选的比例 [1] | 联网检索 / 依赖的索引 |
|---|---|---|---|
| ChatGPT | OpenAI | 79% / 63% | 能联网；用 OAI-SearchBot 抓取页面进入 ChatGPT 搜索结果，屏蔽它的网站不会出现在搜索回答中 [8] |
| Gemini | Google | 31% / 13% | 来源中未说明检索索引 |
| Le Chat（Mistral，2026-05-28 起改名 Vibe，仍在 chat.mistral.ai）[5] | Mistral AI（法国） | 14% / 6%；60–69 岁人群中 22% 使用 | 2025 年起用 Brave Search API 提供实时网页结果 [7]；Mistral 现行爬虫文档称其自建搜索索引供 Vibe 回答问题 [6] |
| Microsoft Copilot | Microsoft | 12% / 5% | 开启网页搜索时向 Bing 搜索服务发送生成的查询 [9] |
| Perplexity / Claude | 各家 | 较少（图表中约 5% / 4%） | — |

- 注意：CRÉDOC 数据的调查时间是 2025 年 6 月，2026 年的变化需以更新调查为准。
- 网页引荐流量口径（Statcounter）：2026 年 9 月 ChatGPT 78.98%、Gemini 11.83%、Perplexity 4.69%、Copilot 2.7%、Claude 1.8%；10 月骤变为 ChatGPT 42.89%、Gemini 36.78%、Perplexity 12.08%，与此前各月差距过大，可能是统计口径变化，引用时同时注明两个月 [2]。
- Google 的 AI 摘要（Aperçus IA，即 AI Overviews）和 Mode IA（AI Mode）在法国上线较晚，2026-07-22 才正式推出，桌面、移动和 Google App 均可用 [4]。

## 3. 搜索引擎与 AI 的关系

- 搜索份额（Statcounter，全设备，2026 年 10 月）：Google 89.31%、Bing 5.13%、Yahoo! 2.32%、Ecosia 1.22%、Qwant 0.76%、DuckDuckGo 0.72% [3]。Qwant 是法国本土搜索引擎，但份额不到 1%。
- 依赖关系：Aperçus IA / Mode IA 基于 Google 搜索索引，页面须可被编入索引并可显示摘要 [10]；Copilot 用 Bing [9]；ChatGPT 搜索依赖 OAI-SearchBot [8]；Mistral Vibe 早期用 Brave，现有自建索引 [6][7]。
- 法国特有：Google 在法国 Search Console 中新增控件，网站可选择是否出现在搜索的生成式 AI 功能中；Google 称该设置不作为普通搜索结果的排名信号 [4]。审计时应询问客户是否启用了这一退出设置——启用后不会出现在 Aperçus IA / Mode IA 中。

## 4. 本地爬虫

无，主要依赖全球通用爬虫。

## 5. 站外重点平台

- 百科：Ahrefs 统计（2026 年 1 月法国数据）中，Wikipédia 是 ChatGPT 在法国引用最多的域名（4.88%），以法语版为主，也引用英文版；Copilot 中 Wikipédia 也居首（5.46%）；Perplexity 中 YouTube 居首（7.16%）[11]。
- 媒体与评测（Ahrefs 2026 年 10 月，ChatGPT 法国回答中被引用的媒体前 50，按引用回答数）[12]：
  - 消费者测评：quechoisir.org（UFC-Que Choisir）第 2（14,828）；部分测试详情需付费订阅。
  - 数码评测：frandroid.com 第 5、lesnumeriques.com 第 10、clubic.com 第 16、01net.com 第 22、jeuxvideo.com 第 23。
  - 汽车：largus.fr 第 1（15,767）、caradisiac.com 第 9、autoplus.fr 第 13。
  - 综合与生活：journaldesfemmes.fr、lemonde.fr、leparisien.fr、lefigaro.fr、linternaute.fr、ouest-france.fr、allocine.fr、santemagazine.fr。
  - 按集团看，Reworld Media（Les Numériques、Auto Plus 等）、Argus 集团、UFC-Que Choisir 占比最高 [12]。
- 电商：ChatGPT 法国回答也会引用 Amazon 以及 Fnac、Darty 等法国零售商 [11]。

## 6. 用户提问方式

| 阶段 | 法语问句 | 中文译文 |
|---|---|---|
| 认知 | Quelle est la différence entre `<品类>` A et B ? | `<品类>` A 和 B 有什么区别？ |
| 认知 | Comment bien choisir son `<品类>` ? | 怎么挑选 `<品类>`？ |
| 对比 | Quel est le meilleur `<品类>` en 2026 selon Que Choisir ? | 按 Que Choisir 的评测，2026 年最好的 `<品类>` 是哪款？ |
| 对比 | `<品牌>` ou `<品牌>` : lequel choisir pour `<用途>` ? | `<品牌>` 和 `<品牌>`，做 `<用途>` 选哪个？ |
| 对比 | Test et avis `<型号>` | `<型号>` 测评和口碑 |
| 决策 | Où acheter `<型号>` au meilleur prix ? | 在哪里买 `<型号>` 最划算？ |
| 决策 | `<品牌>` est-il fiable ? Avis clients | `<品牌>` 靠谱吗？用户评价如何？ |
| 售后 | Comment faire jouer la garantie de `<型号>` ? | `<型号>` 怎么申请保修？ |
| 售后 | Comment retourner un produit `<品牌>` et être remboursé ? | `<品牌>` 的商品怎么退货退款？ |

## 7. 本地化检查要点

- 价格：欧盟规定售价指含增值税及其他税费的最终价格 [16]；检查价格是否写在 HTML 明文里，运费是否单独说明。
- 数字与货币格式：小数点用逗号，千分位用窄不换行空格（U+202F），货币符号在数字后，例如 `1 234,56 €` [17]。检查是否误用英文格式 `€1,234.56`。
- 日期格式：`16/11/2026`（日/月/年），长格式如 `16 nov. 2026` [17]。
- Mentions légales：依 2004 年 LCEN，经营性网站必须提供法定信息并便于查找，可单独成页或放在 CGV 中；内容包括公司名称、法律形式与注册资本（个体经营者写姓名并注明 "EI"）、地址、联系邮箱与电话、RCS / RNE 注册号、增值税号（适用时）、网站托管方的名称、地址和电话等 [13]。检查页脚是否有 "Mentions légales" 链接。
- 个人数据：按 GDPR 第 13 条告知数据处理情况 [15]，通常为单独的 "Politique de confidentialité" 页面。
- Cookie 同意（CNIL）：在用户同意前不得放置或读取需同意的 Cookie；接受 CGU 不算有效同意；"拒绝"必须和"接受"一样简单；撤回同意也要和给出同意一样简单。存储选择、登录、购物车等必要追踪器免于同意 [14]。检查横幅首层是否有与"Tout accepter"同等显眼的"Tout refuser"。

## 8. 证据适用性

推断，证据较弱。`evidence.md` 中的研究几乎全部基于英文 / 美国市场，没有直接以法语或法国用户为对象的受控实验。可参考的当地资料只有观察性数据：CRÉDOC 使用调查 [1]、Statcounter 流量份额 [2][3]、Ahrefs 法国 ChatGPT 引用统计 [11][12]，可作为 E12（第三方来源）和 E13（语言间来源生态不同）在法国的旁证，但不能证明因果。另外 Aperçus IA 在法国 2026 年 7 月才上线 [4]，当地的长期数据更少。

## 9. 来源

1. CRÉDOC：Baromètre du numérique – Édition 2026（Rapport，2026 年 2 月，第 1.6 节）— https://www.arcep.fr/uploads/tx_gspublication/barometre-du-numerique-edition-2026_RAPPORT.pdf （访问 2026-11-16）
2. Statcounter：AI Chatbot Market Share France — https://gs.statcounter.com/ai-chatbot-market-share/all/france （访问 2026-11-16）
3. Statcounter：Search Engine Market Share France — https://gs.statcounter.com/search-engine-market-share/all/france （访问 2026-11-16）
4. Google France：Lancement des Aperçus IA et du Mode IA dans la Recherche Google en France（2026-07-22）— https://blog.google/intl/fr-fr/nouveautes-produits/explorez-obtenez-des-reponses/recherche-ia-apercus-mode/ （访问 2026-11-16）
5. Mistral AI：Vibe gets to work.（2026-05-28）— https://mistral.ai/news/vibe-agent （访问 2026-11-16）
6. Mistral AI Docs：Robots — https://docs.mistral.ai/robots （访问 2026-11-16）
7. TechCrunch：Anthropic appears to be using Brave to power web search for its Claude chatbot（2025-03-21，提及 Le Chat 使用 Brave Search API）— https://techcrunch.com/2025/03/21/anthropic-appears-to-be-using-brave-to-power-web-searches-for-its-claude-chatbot/ （访问 2026-11-16）
8. OpenAI：Overview of OpenAI Crawlers — https://developers.openai.com/api/docs/bots （访问 2026-11-16）
9. Microsoft Learn：Manage web search in Microsoft 365 Copilot — https://learn.microsoft.com/en-us/copilot/microsoft-365/manage-public-web-access （访问 2026-11-16）
10. Google Search Central：AI features and your website — https://developers.google.com/search/docs/appearance/ai-features （访问 2026-11-16）
11. Ahrefs：Les domaines les plus mentionnés par les IA en France et dans le monde（2026-02-19）— https://ahrefs.com/fr/blog/top-domaines-cites-par-ia/ （访问 2026-11-16）
12. Ahrefs：RP : Les 50 médias à cibler pour apparaître dans ChatGPT (France)（2026-10-07 更新）— https://ahrefs.com/fr/blog/medias-a-cibler-pour-apparaitre-dans-chatgpt/ （访问 2026-11-16）
13. Entreprendre Service-Public：Mentions obligatoires sur le site internet d'une entreprise（F37351）— https://entreprendre.service-public.gouv.fr/vosdroits/F37351 （访问 2026-11-16）
14. CNIL：Cookies et traceurs : que dit la loi ? — https://www.cnil.fr/fr/cookies-et-autres-traceurs/regles/cookies/que-dit-la-loi （访问 2026-11-16）
15. EUR-Lex：Regulation (EU) 2016/679（GDPR）— https://eur-lex.europa.eu/eli/reg/2016/679/oj （访问 2026-11-16）
16. EUR-Lex：Directive 98/6/EC on consumer protection in the indication of the prices — https://eur-lex.europa.eu/eli/dir/1998/6/oj （访问 2026-11-16）
17. Unicode CLDR（cldr-json）：fr numbers.json 与 ca-gregorian.json — https://github.com/unicode-org/cldr-json/tree/main/cldr-json/cldr-numbers-full/main/fr ；https://github.com/unicode-org/cldr-json/tree/main/cldr-json/cldr-dates-full/main/fr （访问 2026-11-16）
