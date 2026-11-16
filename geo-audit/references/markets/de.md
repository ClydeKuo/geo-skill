# 市场档案：德国（de）

## 1. 基本信息

- 市场代码：de
- 语言标签：de-DE
- 核对日期：2026-11-16
- 适用范围：德国（德语）。奥地利、瑞士德语区走 `_generic`，可参考本档案：语言和大部分站外平台相近，但搜索份额、法律页面（奥地利 ECG / 瑞士 UWG 等）和货币（瑞士用 CHF）要按当地另行核实，本档案没有覆盖。

## 2. 主流 AI 助手与 AI 搜索

按 Bitkom 2026 年人口调查（16 岁以上 1,003 人，电话访问，2026 年第 8–11 周；58% 的人用 AI，34% 每周至少用一次）中 AI 用户的使用比例排序 [1][2]：

| 产品 | 运营方 | AI 用户中的使用比例 [1][2] | 联网检索 / 依赖的索引 |
|---|---|---|---|
| ChatGPT | OpenAI | 71% | 能联网；用 OAI-SearchBot 抓取页面进入 ChatGPT 搜索结果，屏蔽它的网站不会出现在搜索回答中 [9] |
| Gemini | Google | 50% | 来源中未说明检索索引 |
| Microsoft Copilot | Microsoft | 43% | 开启网页搜索时向 Bing 搜索服务发送生成的查询 [10] |
| Meta AI（WhatsApp 内） | Meta | 35% | 来源中未说明检索索引 |
| DeepSeek / Perplexity / Grok / Claude | 各家 | 8% / 7% / 6% / 5% | — |
| LeChat（Mistral，2026 年 5 月起改名 Vibe） | Mistral AI | 4%；77% 的 AI 用户不知道它 | Bitkom 称欧洲产品"只是小角色" [2] |

- Perplexity 另有运营商渠道：德国电信（Telekom）在 MeinMagenta App 中以"Magenta AI"名义向其客户免费提供 Perplexity [8]。
- 网页引荐流量口径（Statcounter，统计 AI 聊天产品给网站带来的访问）：2026 年 9 月 ChatGPT 78.93%、Gemini 11.3%、Perplexity 5.27%、Copilot 3.06%；10 月数据骤变为 ChatGPT 40.9%、Gemini 35.3%、Perplexity 16.08%，与此前各月差距过大，可能是统计口径变化，引用时同时注明两个月 [3]。
- Google AI Overviews 2025 年 3 月起在德国面向已登录的 18 岁以上用户提供德语和英语版本 [5]；AI Mode 2025 年 10 月扩展到德国并支持德语 [6][7]。

## 3. 搜索引擎与 AI 的关系

- 搜索份额（Statcounter，全设备，2026 年 10 月）：Google 88.46%、Bing 6.39%、Yahoo! 1.61%、Yandex 1.36%、DuckDuckGo 0.99%、Ecosia 0.92% [4]。
- 依赖关系：Google AI Overviews / AI Mode 基于 Google 搜索索引，页面须可被 Googlebot 抓取并编入索引 [11]；Copilot 用 Bing [10]；ChatGPT 搜索依赖自家 OAI-SearchBot 抓取 [9]。因此检查 Googlebot、Bingbot、OAI-SearchBot 的可抓取性是德国站的基本要求。
- 德国特有：AI Overviews 在德国仅对已登录的成年用户显示 [5]；实测时应登录 18 岁以上的 Google 账号并把语言设为德语。

## 4. 本地爬虫

无，主要依赖全球通用爬虫。

## 5. 站外重点平台

依据 Ahrefs Brand Radar 对德国 ChatGPT 联网回答的统计（2026 年 10 月数据，前 50 个域名合计 460,416 次引用）[12]：

- 百科与词典：de.wikipedia.org 第 1（15.78%），en.wikipedia.org 第 3（4.59%），duden.de 第 4（4.51%）。德语 Wikipedia 条目是首要的站外建设对象。
- 消费者测评与比价：test.de（Stiftung Warentest）第 5（3.85%）、verbraucherzentrale.de 第 6（3.05%）、idealo.de 第 9（2.59%）、chip.de 第 14、computerbild.de 第 16、finanztip.de 第 27。test.de 的大部分测试结果需付费才能看全文。
- 点评：de.trustpilot.com 第 11（2.24%）。
- 行业 / 垂直站：adac.de 第 2（汽车，6.45%）、autobild.de、autoscout24.de；健康类 gesund.bund.de、apotheken-umschau.de；法律条文 gesetze-im-internet.de 第 10。
- 媒体：faz.net 第 7、ndr.de、welt.de。
- 零售官网也会被引：dm.de、rewe.de、obi.de、ikea.com。
- 该统计中前 50 没有 YouTube、Reddit、LinkedIn、Instagram [12]，与英文市场差别明显。

## 6. 用户提问方式

| 阶段 | 德语问句 | 中文译文 |
|---|---|---|
| 认知 | Was ist der Unterschied zwischen `<品类>` A und B? | `<品类>` A 和 B 有什么区别？ |
| 认知 | Worauf sollte man beim Kauf von `<品类>` achten? | 买 `<品类>` 要注意什么？ |
| 对比 | Welche `<品类>` sind laut Stiftung Warentest die besten 2026? | 按 Stiftung Warentest 的结果，2026 年最好的 `<品类>` 有哪些？ |
| 对比 | `<品牌>` oder `<品牌>`: Was ist besser für `<用途>`? | `<品牌>` 还是 `<品牌>`，做 `<用途>` 哪个更好？ |
| 对比 | `<型号>` Test und Erfahrungen | `<型号>` 测评和使用体验 |
| 决策 | Wo kann ich `<型号>` am günstigsten kaufen? | 哪里买 `<型号>` 最便宜？ |
| 决策 | Ist `<品牌>` seriös? Erfahrungen mit dem Onlineshop | `<品牌>` 靠谱吗？这家网店的口碑如何？ |
| 售后 | `<型号>` Garantie oder Gewährleistung – was gilt? | `<型号>` 的厂家保修和法定保修各是怎么规定的？ |
| 售后 | Wie kann ich bei `<品牌>` widerrufen und zurücksenden? | 在 `<品牌>` 怎么撤销订单并退货？ |

## 7. 本地化检查要点

- 价格：向消费者报价必须标明总价（Gesamtpreis）[16]；欧盟规定售价指含增值税及其他税费的最终价格 [17]。检查商品页是否有"inkl. MwSt."及运费说明，价格是否写在 HTML 明文里。
- 数字与货币格式：德语小数点用逗号、千分位用句点，货币符号在数字后，例如 `1.234,56 €` [18]。
- 日期格式：`16.11.2026`（日.月.年）[18]。
- Impressum：商业网站必须提供易于识别、可直接访问、始终可用的提供者信息（名称、地址、快速联系方式含电子邮件、商业登记号、增值税号等）[13]。检查每页页脚是否有 Impressum 链接。
- Datenschutzerklärung：按 GDPR 第 13 条告知数据处理情况 [14]，通常单独成页，链接放在页脚。
- Cookie 同意：在终端设备上存取信息须事先取得用户同意，技术上必需的除外 [15]。检查同意横幅是否在加载跟踪脚本之前出现，是否提供"拒绝"选项。
- 支付说明：德国线上营业额中 PayPal 占 28.7%、发票后付（Kauf auf Rechnung）占 26.1%、直接借记（Lastschrift）14.4%、信用卡等 13.7%（EHI Online-Payment 2026，2025 年数据）[19]。支付页或 FAQ 中应写明是否支持这些方式。

## 8. 证据适用性

推断，证据较弱。`evidence.md` 中的研究几乎全部基于英文 / 美国市场，没有直接以德语或德国用户为对象的受控实验。可参考的当地资料只有观察性数据：Bitkom 使用调查 [1][2]、Statcounter 流量份额 [3][4]、Ahrefs 德国 ChatGPT 引用域名统计 [12]；其中 Ahrefs 的数据支持 E12（第三方来源）和 E13（不同语言的来源生态不同）在德国同样成立，但不能证明因果。

## 9. 来源

1. Bitkom：Ein Drittel nutzt KI mindestens einmal pro Woche – von Code bis Küche（2026-04-28）— https://www.bitkom.org/Presse/Presseinformation/Ein-Drittel-nutzt-KI-mindestens-einmal-pro-Woche （访问 2026-11-16）
2. Bitkom：Künstliche Intelligenz in Deutschland – Wie die Bevölkerung auf die neue Technologie blickt（Studienbericht 2026，图 10）— https://www.bitkom.org/sites/main/files/2026-06/bitkom-studienbericht-ki-bevoelkerung.pdf （访问 2026-11-16）
3. Statcounter：AI Chatbot Market Share Germany — https://gs.statcounter.com/ai-chatbot-market-share/all/germany （访问 2026-11-16）
4. Statcounter：Search Engine Market Share Germany — https://gs.statcounter.com/search-engine-market-share/all/germany （访问 2026-11-16）
5. Google：We're bringing the helpfulness of AI Overviews to more countries in Europe — https://blog.google/feed/were-bringing-the-helpfulness-of-ai-overviews-to-more-countries-in-europe/ （访问 2026-11-16）
6. Google：AI Mode is now available in more languages and locations around the world（2025-10-07）— https://blog.google/products-and-platforms/products/search/ai-mode-expands-languages-locations/ （访问 2026-11-16）
7. Search Engine Roundtable：Google AI Mode Expands To 35 New Languages & 40 Countries（国家与语言清单）— https://www.seroundtable.com/google-ai-mode-expands-40232.html （访问 2026-11-16）
8. Deutsche Telekom：KI für alle – Perplexity jetzt unter „Magenta AI" in der MeinMagenta-App — https://www.telekom.com/de/medien/medieninformationen/detail/perplexity-jetzt-in-der-meinmagenta-app-1083474 （访问 2026-11-16）
9. OpenAI：Overview of OpenAI Crawlers — https://developers.openai.com/api/docs/bots （访问 2026-11-16）
10. Microsoft Learn：Manage web search in Microsoft 365 Copilot — https://learn.microsoft.com/en-us/copilot/microsoft-365/manage-public-web-access （访问 2026-11-16）
11. Google Search Central：AI features and your website — https://developers.google.com/search/docs/appearance/ai-features （访问 2026-11-16）
12. Ahrefs：Die 50 meistzitierten Domains in ChatGPT in Deutschland（2026-11-01 更新，10 月数据）— https://ahrefs.com/de/blog/chatgpt-deutschland-meistzitierte-domains/ （访问 2026-11-16）
13. § 5 DDG（Digitale-Dienste-Gesetz）Allgemeine Informationspflichten — https://www.gesetze-im-internet.de/ddg/__5.html （访问 2026-11-16）
14. EUR-Lex：Regulation (EU) 2016/679（GDPR）— https://eur-lex.europa.eu/eli/reg/2016/679/oj （访问 2026-11-16）
15. § 25 TDDDG：Schutz der Privatsphäre bei Endeinrichtungen — https://www.gesetze-im-internet.de/ttdsg/__25.html （访问 2026-11-16）
16. § 3 PAngV：Pflicht zur Angabe des Gesamtpreises — https://www.gesetze-im-internet.de/pangv_2022/__3.html （访问 2026-11-16）
17. EUR-Lex：Directive 98/6/EC on consumer protection in the indication of the prices — https://eur-lex.europa.eu/eli/dir/1998/6/oj （访问 2026-11-16）
18. Unicode CLDR（cldr-json）：de numbers.json 与 ca-gregorian.json — https://github.com/unicode-org/cldr-json/tree/main/cldr-json/cldr-numbers-full/main/de ；https://github.com/unicode-org/cldr-json/tree/main/cldr-json/cldr-dates-full/main/de （访问 2026-11-16）
19. IT Finanzmagazin：Online-Payment: Rechnungskauf und PayPal weiter dominierend, laut EHI-Studie „Online-Payment 2026" — https://www.it-finanzmagazin.de/online-payment-rechnungskauf-und-paypal-weiter-dominierend-laut-ehi-studie-online-payment-2026-244098/ （访问 2026-11-16）
