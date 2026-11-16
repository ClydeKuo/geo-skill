# geo-audit

[简体中文](README.md) | **English** | [日本語](README.ja.md) | [한국어](README.ko.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Español](README.es.md)

A skill in the open Agent Skills format. Given only a URL, it audits a website from the outside for its visibility in AI search across one or more countries / language markets (ChatGPT, Perplexity, Google AI Overviews, Gemini, Copilot, Doubao, DeepSeek, Naver AI Briefing, Le Chat, etc.) and produces an optimization report in which every recommendation is graded by research evidence. The report is written in the language the user asked in.

- Profiled markets: China `cn`, United States `us`, Japan `jp`, South Korea `kr`, Germany `de`, France `fr`, Spanish-speaking markets `es`; all other markets use the generic profile

## Installation

```bash
# Install into the current repo (Claude Code reads .claude/skills; Codex and Cursor read .agents/skills)
bash geo-audit/install.sh

# Install into your home directory for all projects
bash geo-audit/install.sh --user

# Install into another project
bash geo-audit/install.sh --project /path/to/project

# Also link into Cursor's own .cursor/skills (usually unnecessary; Cursor also reads .agents/skills and .claude/skills)
bash geo-audit/install.sh --tools claude,agents,cursor
```

The installer only creates symlinks; existing files or directories with the same name are never overwritten.

## Using it in each tool

Just ask in natural language, for example: "Run a GEO audit of https://example.com for the Japanese and US markets"

| Tool | Notes |
|---|---|
| Claude Code | Works out of the box. |
| Codex CLI | Enable web search and sandbox network access, otherwise the scripts cannot fetch pages and the off-site section cannot be checked: `codex --search exec -s workspace-write -c sandbox_workspace_write.network_access=true "<your request>"` (Interactive mode works the same way: `codex --search -s workspace-write -c sandbox_workspace_write.network_access=true`) |
| Cursor | Install following Cursor's documented directories (`.agents/skills` / `.claude/skills` / `.cursor/skills`). **Not yet tested in Cursor.** |

## Requirements

- Python 3.10+ (standard library only)
- Optional: Chrome / Chromium for the rendering comparison; set `GEO_BROWSER` to point to a specific browser

## Running the scripts directly

```bash
python3 geo-audit/scripts/crawl_check.py https://example.com --markets jp,us
python3 geo-audit/scripts/page_audit.py https://example.com/ja/ --lang ja-JP --save-html out/html
python3 geo-audit/scripts/render_diff.py https://example.com/ja/ --lang ja-JP --timeout 30
# To test reachability from a country, you may use an exit proxy in that country (never to evade rate limits)
python3 geo-audit/scripts/crawl_check.py https://example.com --proxy http://<proxy-host>:<port>
```

## Tests

```bash
python3 -m unittest discover -s geo-audit/tests -v
```
