# 市场档案：西班牙语地区（es）

## 1. 基本信息

- 市场代码：es
- 语言标签：es（分列西班牙 es-ES 与拉美 es-419）
- 核对日期：2026-11-16
- 适用范围：西班牙（es-ES）为主，拉美西语国家（es-419）在各节单列差异。可达性测试默认按西班牙（请求语言 es-ES、欧元价格）。拉美各国的搜索份额、法律页面、货币和数字格式不一致，本档案只以墨西哥为例补充少量数据，其他国家要按当地另行核实；巴西为葡萄牙语，不适用本档案。

## 2. 主流 AI 助手与 AI 搜索

### 西班牙（es-ES）

- 整体使用：INE 2026 年调查显示，16–74 岁人群中 54.8% 在最近三个月用过生成式 AI 工具，比 2025 年高 16.9 个百分点 [2]。CNMC 家庭面板（2026 年第二季度，6,009 户、8,853 人）显示约一半网民经常使用生成式 AI 应用 [1]。

| 产品 | 运营方 | 经常使用的网民比例（CNMC）[1] | AI 用户中当前使用 / 首选（IAB Spain）[3] | 联网检索 / 依赖的索引 |
|---|---|---|---|---|
| ChatGPT | OpenAI | 41.3% | 70% / 52% | 能联网；用 OAI-SearchBot 抓取页面进入 ChatGPT 搜索结果，屏蔽它的网站不会出现在搜索回答中 [11] |
| Gemini / NotebookLM | Google | 17.2% | 43% / 24% | 来源中未说明检索索引 |
| Microsoft Copilot | Microsoft | 7.1% | 第三 | 开启网页搜索时向 Bing 搜索服务发送生成的查询 [12] |

- CNMC：只有 8.6% 的 AI 用户付费；38.9% 比较或非常信任回答，84.1% 至少核对过一次回答是否属实 [1]。
- 网页引荐流量口径（Statcounter）：2026 年 9 月 ChatGPT 77.56%、Gemini 14.62%、Perplexity 3.94%、Copilot 2.79%；10 月骤变为 Gemini 44.32%、ChatGPT 41.46%、Perplexity 9.27%，与此前各月差距过大，可能是统计口径变化，引用时同时注明两个月 [4]。
- Google AI Overviews 2025 年 3 月起在西班牙面向已登录的 18 岁以上用户提供西班牙语和英语版本 [8]；AI Mode 2025 年 10 月扩展到西班牙并支持西班牙语 [9][10]。

### 拉美（es-419）

- 网页引荐流量口径（Statcounter，墨西哥）：2026 年 9 月 ChatGPT 70.87%、Gemini 21.5%、Copilot 3.97%、Perplexity 3.18%；10 月骤变为 Gemini 53.76%、ChatGPT 35.28%、Perplexity 6.08%，同样可能是统计口径变化 [5]。
- 未找到覆盖拉美普通人群、方法透明的 2026 年 AI 工具使用调查，因此不列使用比例。
- Google AI Overviews 自 2024 年 10 月起支持西班牙语，用户可在有该功能的国家选择西班牙语 [13]。

## 3. 搜索引擎与 AI 的关系

- 西班牙搜索份额（Statcounter，全设备，2026 年 10 月）：Google 93.3%、Bing 3.91%、Yahoo! 2%、DuckDuckGo 0.39%、Ecosia 0.2% [6]。
- 墨西哥搜索份额（同口径）：Google 86.59%、Bing 10.63%、Yahoo! 2.14% [7]。墨西哥 Bing 份额明显高于西班牙，Copilot 依赖 Bing [12]，墨西哥站更要检查 Bingbot 是否可抓取。
- 依赖关系：AI Overviews / AI Mode 基于 Google 搜索索引，页面须可被编入索引并可显示摘要 [14]；ChatGPT 搜索依赖 OAI-SearchBot [11]。
- 西班牙的 AI Overviews 仅对已登录的成年用户显示 [8]，实测时应登录 18 岁以上的 Google 账号并把语言设为西班牙语。

## 4. 本地爬虫

无，主要依赖全球通用爬虫。

## 5. 站外重点平台

### 西班牙（es-ES）

- 百科与词典：es.wikipedia.org 是 Gemini 西班牙回答中引用最多的域名（2026 年 11 月数据，21,027 次回答），en.wikipedia.org 第 3 [17]；在 AI Overviews 西班牙数据中 es.wikipedia.org 第 5，dle.rae.es（西班牙皇家学院词典）第 7 [16]。
- 视频与社交：AI Overviews 西班牙前 4 位是 youtube.com、instagram.com、facebook.com、tiktok.com，reddit.com 第 6 [16]；Gemini 中 reddit.com 第 2、youtube.com 第 4 [17]。Ahrefs 作者称 ChatGPT 中 Reddit 进不了前 20 [17]。
- 数码评测：xataka.com 在 Gemini 西班牙第 9（4,198）[17]、AI Overviews 第 27 [16]。
- 消费者组织：ocu.org（OCU）在 Gemini 西班牙第 49 [17]、AI Overviews 第 63 [16]；部分测试结果需会员登录查看。
- 比价与零售：idealo.es 在 Gemini 西班牙第 5、elcorteingles.es 第 10、pccomponentes.com 第 12 [17]；amazon.es 在 AI Overviews 第 9 [16]。
- 垂直站：汽车 coches.net、carwow.es、quecochemecompro.com、km77.com；药品 cima.aemps.es；房产 idealista.com；旅游 tripadvisor.es [16][17]。点评：es.trustpilot.com 在 AI Overviews 第 19 [16]。
- 新闻媒体：ChatGPT 西班牙回答中 elpais.com 是整体第 5 的域名（5,806 次），其次是阿根廷媒体 infobae.com（2,319）、lavanguardia.com；Gemini 中 elespanol.com 在媒体中领先；AI Mode 中 elmundo.es 排媒体第 2 [15]。

### 拉美（es-419）

- 未找到以拉美西语用户为对象的 AI 引用域名统计。
- 线索：infobae.com（阿根廷）在 ChatGPT 西班牙回答中也被大量引用，说明西语来源跨国流通 [15]；区域电商平台 Mercado Libre 在 18 个拉美国家运营 [24]，但未找到它被 AI 引用的西语数据（Gemini 全球榜上只出现巴西葡语站 mercadolivre.com.br）[17]。

## 6. 用户提问方式

| 阶段 | 西班牙语问句 | 中文译文 |
|---|---|---|
| 认知 | ¿Qué diferencia hay entre `<品类>` A y B? | `<品类>` A 和 B 有什么区别？ |
| 认知 | ¿Qué tener en cuenta al comprar un `<品类>`? | 买 `<品类>` 要注意什么？ |
| 对比 | ¿Cuál es el mejor `<品类>` calidad-precio en 2026? | 2026 年性价比最高的 `<品类>` 是哪款？ |
| 对比 | `<品牌>` o `<品牌>`: ¿cuál es mejor para `<用途>`? | `<品牌>` 和 `<品牌>`，做 `<用途>` 哪个更好？ |
| 对比 | `<型号>` análisis y opiniones | `<型号>` 测评和评价 |
| 决策 | ¿Dónde comprar `<型号>` más barato? | 在哪里买 `<型号>` 最便宜？ |
| 决策 | ¿Es fiable `<品牌>`? Opiniones de clientes | `<品牌>` 靠谱吗？顾客怎么说？ |
| 售后 | ¿Cómo funciona la garantía de `<型号>`? | `<型号>` 的保修怎么用？ |
| 售后 | ¿Cómo devolver un producto a `<品牌>` y pedir el reembolso? | 怎么把商品退回给 `<品牌>` 并申请退款？ |

以上问句按西班牙写法；面向拉美时，实测前应按目标国家的真实问法调整。

## 7. 本地化检查要点

### 西班牙（es-ES）

- 价格：LSSI 第 10 条要求网站清楚准确地标明价格，并说明是否含税及运费 [18]；欧盟规定售价指含增值税及其他税费的最终价格 [21]。检查商品页是否注明 "IVA incluido" 和运费。
- 数字与货币格式：小数点用逗号、千分位用句点，货币符号在数字后，例如 `1.234,56 €`；按 CLDR 规则，四位数通常不加千分位（`1234`），五位数起才加（`12.345`）[22]。
- 日期格式：`16/11/2026`（日/月/年），长格式如 `16 nov 2026` [22]。
- Aviso legal：LSSI 第 10 条要求以永久、便捷、直接、免费的方式提供名称或公司名称、地址、电子邮件、商业登记信息、NIF（税号）、需许可活动的许可信息、受监管职业信息、价格信息和所加入的行为准则；放在网站上即可满足 [18]。检查页脚是否有 "Aviso legal" 链接。
- 个人数据：按 GDPR 第 13 条告知数据处理情况 [20]，通常为 "Política de privacidad" 页面。
- Cookie 同意：LSSI 第 22.2 条要求在终端存取数据前取得用户同意，仅用于传输通信或提供用户明确请求的服务所严格必需的除外 [18]；AEPD 发布有 Cookie 使用指南 [19]。检查横幅是否先于跟踪脚本出现、是否能拒绝。
- 支付：Bizum 成立十周年（2026 年 10 月）时有 3,250 万用户；2019 年开通电商支付以来累计线上购物超过 3.2 亿笔，接受 Bizum 的网店和公共机构约 12 万家 [23]。支付说明中应写明是否支持 Bizum。

### 拉美（es-419）

- 数字与货币格式因国而异：墨西哥（es-MX）及 CLDR 的 es-419 通用规则用小数点、逗号作千分位，货币符号在前（`$1,234.56`）；阿根廷、哥伦比亚、智利用逗号作小数点、句点作千分位（`$ 1.234,56`）[22]。很多国家都用 "$"，应写明币种代码（MXN、ARS、COP 等）。
- 日期格式：墨西哥短格式 `16/11/26`（日/月/年）[22]。
- 墨西哥价格：《联邦消费者保护法》第 7 Bis 条要求显著标明应付总额，包括税费、佣金、利息、保险及其他附加费用 [25]。
- 其他国家的法律页面、Cookie 规则和本地支付方式本档案未覆盖，需按国别另行核实。

## 8. 证据适用性

推断，证据较弱。`evidence.md` 中的研究几乎全部基于英文 / 美国市场，没有直接以西班牙语用户为对象的受控实验。西班牙有较多观察性当地资料：CNMC、INE、IAB Spain 的使用调查 [1][2][3]，Ahrefs 西班牙的 ChatGPT / Gemini / AI Overviews 引用统计 [15][16][17]，可作为 E12（第三方来源）和 E13（不同引擎、不同语言来源差异大）的旁证，但不能证明因果。拉美基本没有可参考的当地研究，证据更弱。

## 9. 来源

1. CNMC：La mitad de los internautas utilizó habitualmente herramientas de inteligencia artificial（2026-11-06）— https://www.cnmc.es/prensa/panel-hogares-inteligencia-artificial-20261106 （访问 2026-11-16）
2. INE：Encuesta sobre Equipamiento y Uso de Tecnologías de Información y Comunicación en los Hogares, Año 2026 — https://www.ine.es/dyngs/Prensa/TICH2026.htm （访问 2026-11-16）
3. IAB Spain：I Estudio de Inteligencia Artificial 2026（与 Elogia 合作）— https://iabspain.es/estudio/i-estudio-inteligencia-artificial-iab-spain-2026/ （访问 2026-11-16）
4. Statcounter：AI Chatbot Market Share Spain — https://gs.statcounter.com/ai-chatbot-market-share/all/spain （访问 2026-11-16）
5. Statcounter：AI Chatbot Market Share Mexico — https://gs.statcounter.com/ai-chatbot-market-share/all/mexico （访问 2026-11-16）
6. Statcounter：Search Engine Market Share Spain — https://gs.statcounter.com/search-engine-market-share/all/spain （访问 2026-11-16）
7. Statcounter：Search Engine Market Share Mexico — https://gs.statcounter.com/search-engine-market-share/all/mexico （访问 2026-11-16）
8. Google：We're bringing the helpfulness of AI Overviews to more countries in Europe — https://blog.google/feed/were-bringing-the-helpfulness-of-ai-overviews-to-more-countries-in-europe/ （访问 2026-11-16）
9. Google：AI Mode is now available in more languages and locations around the world（2025-10-07）— https://blog.google/products-and-platforms/products/search/ai-mode-expands-languages-locations/ （访问 2026-11-16）
10. Search Engine Roundtable：Google AI Mode Expands To 35 New Languages & 40 Countries（国家与语言清单）— https://www.seroundtable.com/google-ai-mode-expands-40232.html （访问 2026-11-16）
11. OpenAI：Overview of OpenAI Crawlers — https://developers.openai.com/api/docs/bots （访问 2026-11-16）
12. Microsoft Learn：Manage web search in Microsoft 365 Copilot — https://learn.microsoft.com/en-us/copilot/microsoft-365/manage-public-web-access （访问 2026-11-16）
13. Google：AI Overviews in Google Search expanding to more than 100 countries（2024-10-28）— https://blog.google/products-and-platforms/products/search/ai-overviews-search-october-2024/ （访问 2026-11-16）
14. Google Search Central：AI features and your website — https://developers.google.com/search/docs/appearance/ai-features （访问 2026-11-16）
15. Ahrefs：Cuáles son los medios más citados por la IA en España: ChatGPT, Gemini, Modo IA de Google y más（2026-07-13）— https://ahrefs.com/es/blog/top-medios-citados-ia/ （访问 2026-11-16）
16. Ahrefs：AI Overviews en España: estas son las webs que más aparecen（2025-10-22）— https://ahrefs.com/es/blog/dominios-mas-citados-ai-overviews-espana/ （访问 2026-11-16）
17. Ahrefs：Los 100 dominios más citados por Gemini en España (y en el mundo)（2026 年 11 月数据）— https://ahrefs.com/es/blog/dominios-mas-citados-gemini-espana/ （访问 2026-11-16）
18. BOE：Ley 34/2002, de 11 de julio, de servicios de la sociedad de la información y de comercio electrónico（LSSI，第 10、22 条）— https://www.boe.es/buscar/act.php?id=BOE-A-2002-13758 （访问 2026-11-16）
19. AEPD：Guía sobre el uso de las cookies — https://www.aepd.es/guias/guia-cookies.pdf （访问 2026-11-16）
20. EUR-Lex：Regulation (EU) 2016/679（GDPR）— https://eur-lex.europa.eu/eli/reg/2016/679/oj （访问 2026-11-16）
21. EUR-Lex：Directive 98/6/EC on consumer protection in the indication of the prices — https://eur-lex.europa.eu/eli/dir/1998/6/oj （访问 2026-11-16）
22. Unicode CLDR（cldr-json）：es、es-419、es-MX、es-AR、es-CO、es-CL 的 numbers.json 与 ca-gregorian.json — https://github.com/unicode-org/cldr-json/tree/main/cldr-json/cldr-numbers-full/main ；https://github.com/unicode-org/cldr-json/tree/main/cldr-json/cldr-dates-full/main （访问 2026-11-16）
23. Ecommerce News：Bizum cumple 10 años: 32,5 millones de bizumers y 3,5 millones de operaciones diarias — https://ecommerce-news.es/bizum-cumple-10-anos-325-millones-de-bizumers-y-35-millones-de-operaciones-diarias/ （访问 2026-11-16）
24. MercadoLibre, Inc.：Form 424B2（2026，SEC EDGAR）— https://www.sec.gov/Archives/edgar/data/0001099590/000114036126036202/ny20080683x2_424b2.htm （访问 2026-11-16）
25. Cámara de Diputados：Ley Federal de Protección al Consumidor（第 7 Bis 条）— https://www.diputados.gob.mx/LeyesBiblio/pdf/LFPC.pdf （访问 2026-11-16）
