# geo-audit

一个遵循开放 Agent Skills 格式的 skill：只凭网址，从外部审计网站在一个或多个国家 / 语言市场的 AI 搜索可见度（ChatGPT、Perplexity、Google AI Overviews、Gemini、Copilot、豆包、DeepSeek、Naver AI Briefing、Le Chat 等），输出带论文证据强度的优化报告。报告语言跟随用户提问的语言。

- 已建档市场：中国 `cn`、美国 `us`、日本 `jp`、韩国 `kr`、德国 `de`、法国 `fr`、西班牙语地区 `es`；其他市场走通用档案

## 安装

```bash
# 装到当前仓库（Claude Code 读 .claude/skills，Codex 与 Cursor 读 .agents/skills）
bash geo-audit/install.sh

# 装到用户目录，所有项目可用
bash geo-audit/install.sh --user

# 装到其他项目
bash geo-audit/install.sh --project /path/to/project

# 额外链接到 Cursor 专用目录 .cursor/skills（一般不需要，Cursor 也读 .agents/skills 和 .claude/skills）
bash geo-audit/install.sh --tools claude,agents,cursor
```

安装脚本只建符号链接；已存在的同名文件或目录不会被覆盖。

## 在各工具中使用

用自然语言提出审计请求即可，例如"帮我做一下 https://example.com 的 GEO 审计，目标市场日本和美国"。

| 工具 | 说明 |
|---|---|
| Claude Code | 直接使用。 |
| Codex CLI | 需要开启网页搜索并允许沙箱联网，否则脚本无法抓取、站外一节无法检测：`codex --search exec -s workspace-write -c sandbox_workspace_write.network_access=true "<你的请求>"`（交互模式同理：`codex --search -s workspace-write -c sandbox_workspace_write.network_access=true`）。 |
| Cursor | 按 Cursor 官方目录规则安装（`.agents/skills` / `.claude/skills` / `.cursor/skills`）。**未在 Cursor 中实测。** |

## 依赖

- Python 3.10+（只用标准库）
- 可选：Chrome / Chromium，用于渲染对比；可用环境变量 `GEO_BROWSER` 指定浏览器路径

## 单独运行脚本

```bash
python3 geo-audit/scripts/crawl_check.py https://example.com --markets jp,us
python3 geo-audit/scripts/page_audit.py https://example.com/ja/ --lang ja-JP --save-html out/html
python3 geo-audit/scripts/render_diff.py https://example.com/ja/ --lang ja-JP --timeout 30
# 测试某国可达性时可走该国出口代理（不要用于规避限流）
python3 geo-audit/scripts/crawl_check.py https://example.com --proxy http://<代理地址>:<端口>
```

## 测试

```bash
python3 -m unittest discover -s geo-audit/tests -v
```
