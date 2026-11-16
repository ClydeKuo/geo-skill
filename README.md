# geo-audit

一个 Claude Code agent skill：只凭网址从外部审计网站在 AI 搜索（ChatGPT、Perplexity、Google AI Overview、豆包、DeepSeek 等）中的可见度，输出带论文证据强度的中文 GEO 优化报告。支持国内、海外两个市场。


## 安装

```bash
mkdir -p ~/.claude/skills
ln -s "$PWD/geo-audit" ~/.claude/skills/geo-audit
```

之后在 Claude Code 中说"帮我做一下 https://example.com 的 GEO 审计"即可触发。

## 依赖

- Python 3.10+（只用标准库）
- 可选：Chrome / Chromium，用于渲染对比；也可以用环境变量 `GEO_BROWSER` 指定浏览器路径

## 单独运行脚本

```bash
python3 geo-audit/scripts/crawl_check.py https://example.com
python3 geo-audit/scripts/page_audit.py https://example.com/a https://example.com/b
python3 geo-audit/scripts/render_diff.py https://example.com --timeout 30
# 走代理（例如日本出口）
python3 geo-audit/scripts/crawl_check.py https://example.com --proxy http://proxy.example:8080
```

## 测试

```bash
python3 -m unittest discover -s geo-audit/tests -v
```
