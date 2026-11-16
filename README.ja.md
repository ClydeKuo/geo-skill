# geo-audit

[简体中文](README.md) | [English](README.en.md) | **日本語** | [한국어](README.ko.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | [Español](README.es.md)

オープンな Agent Skills 形式の skill です。URL だけを手がかりに、1 つまたは複数の国・言語市場における AI 検索での見え方（ChatGPT、Perplexity、Google AI Overviews、Gemini、Copilot、Doubao、DeepSeek、Naver AI Briefing、Le Chat など）をサイトの外側から監査し、各提案に研究エビデンスの強さを付けた改善レポートを出力します。レポートはユーザーが質問した言語で書かれます。

- プロファイル済みの市場：中国 `cn`、米国 `us`、日本 `jp`、韓国 `kr`、ドイツ `de`、フランス `fr`、スペイン語圏 `es`。その他の市場は汎用プロファイルを使います

## インストール

```bash
# 現在のリポジトリにインストール（Claude Code は .claude/skills、Codex と Cursor は .agents/skills を読みます）
bash geo-audit/install.sh

# ホームディレクトリにインストール（全プロジェクトで利用可能）
bash geo-audit/install.sh --user

# 別のプロジェクトにインストール
bash geo-audit/install.sh --project /path/to/project

# Cursor 専用の .cursor/skills にも追加でリンク（通常は不要。Cursor は .agents/skills と .claude/skills も読みます）
bash geo-audit/install.sh --tools claude,agents,cursor
```

インストーラーはシンボリックリンクを作るだけで、同名の既存ファイルやディレクトリは上書きしません。

## 各ツールでの使い方

自然な言葉で依頼するだけです。例：「https://example.com の GEO 監査をしてください。対象市場は日本と米国です」

| ツール | 説明 |
|---|---|
| Claude Code | そのまま使えます。 |
| Codex CLI | Web 検索とサンドボックスのネットワークアクセスを有効にしてください。無効だとスクリプトがページを取得できず、サイト外の調査もできません： `codex --search exec -s workspace-write -c sandbox_workspace_write.network_access=true "<依頼内容>"` (対話モードも同様です： `codex --search -s workspace-write -c sandbox_workspace_write.network_access=true`) |
| Cursor | Cursor の公式ディレクトリ規則に従ってインストールします（`.agents/skills` / `.claude/skills` / `.cursor/skills`）。**Cursor では未検証です。** |

## 必要環境

- Python 3.10 以上（標準ライブラリのみ）
- 任意：レンダリング比較用の Chrome / Chromium。環境変数 `GEO_BROWSER` でブラウザのパスを指定できます

## スクリプトを単独で実行する

```bash
python3 geo-audit/scripts/crawl_check.py https://example.com --markets jp,us
python3 geo-audit/scripts/page_audit.py https://example.com/ja/ --lang ja-JP --save-html out/html
python3 geo-audit/scripts/render_diff.py https://example.com/ja/ --lang ja-JP --timeout 30
# 特定の国からの到達性を確認する場合は、その国の出口プロキシを使えます（レート制限の回避には使わないでください）
python3 geo-audit/scripts/crawl_check.py https://example.com --proxy http://<プロキシ>:<ポート>
```

## テスト

```bash
python3 -m unittest discover -s geo-audit/tests -v
```
