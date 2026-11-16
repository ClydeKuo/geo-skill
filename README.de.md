# geo-audit

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | **Deutsch** | [Français](README.fr.md) | [Español](README.es.md)

Ein Skill im offenen Agent-Skills-Format. Anhand einer einzigen URL prüft er von außen, wie sichtbar eine Website in der KI-Suche in einem oder mehreren Ländern bzw. Sprachmärkten ist (ChatGPT, Perplexity, Google AI Overviews, Gemini, Copilot, Doubao, DeepSeek, Naver AI Briefing, Le Chat usw.), und erstellt einen Optimierungsbericht, in dem jede Empfehlung nach Forschungsevidenz bewertet ist. Der Bericht wird in der Sprache verfasst, in der die Anfrage gestellt wurde.

- Märkte mit Profil: China `cn`, USA `us`, Japan `jp`, Südkorea `kr`, Deutschland `de`, Frankreich `fr`, spanischsprachige Märkte `es`; alle anderen Märkte nutzen das allgemeine Profil

## Installation

```bash
# Im aktuellen Repository installieren (Claude Code liest .claude/skills, Codex und Cursor lesen .agents/skills)
bash geo-audit/install.sh

# Im Home-Verzeichnis installieren (für alle Projekte)
bash geo-audit/install.sh --user

# In einem anderen Projekt installieren
bash geo-audit/install.sh --project /path/to/project

# Zusätzlich in Cursors eigenes .cursor/skills verlinken (meist unnötig; Cursor liest auch .agents/skills und .claude/skills)
bash geo-audit/install.sh --tools claude,agents,cursor
```

Das Installationsskript legt nur symbolische Links an; vorhandene Dateien oder Verzeichnisse gleichen Namens werden nie überschrieben.

## Verwendung in den einzelnen Tools

Einfach in natürlicher Sprache anfragen, zum Beispiel: "Bitte führe ein GEO-Audit von https://example.com für den deutschen und den US-Markt durch"

| Tool | Hinweise |
|---|---|
| Claude Code | Funktioniert direkt. |
| Codex CLI | Websuche und Netzwerkzugriff in der Sandbox aktivieren, sonst können die Skripte keine Seiten abrufen und der Abschnitt zu externen Erwähnungen nicht geprüft werden: `codex --search exec -s workspace-write -c sandbox_workspace_write.network_access=true "<deine Anfrage>"` (Im interaktiven Modus genauso: `codex --search -s workspace-write -c sandbox_workspace_write.network_access=true`) |
| Cursor | Installation gemäß den dokumentierten Cursor-Verzeichnissen (`.agents/skills` / `.claude/skills` / `.cursor/skills`). **In Cursor noch nicht getestet.** |

## Voraussetzungen

- Python 3.10+ (nur Standardbibliothek)
- Optional: Chrome / Chromium für den Rendering-Vergleich; mit `GEO_BROWSER` lässt sich ein bestimmter Browser angeben

## Skripte direkt ausführen

```bash
python3 geo-audit/scripts/crawl_check.py https://example.com --markets jp,us
python3 geo-audit/scripts/page_audit.py https://example.com/ja/ --lang ja-JP --save-html out/html
python3 geo-audit/scripts/render_diff.py https://example.com/ja/ --lang ja-JP --timeout 30
# Zum Testen der Erreichbarkeit aus einem Land kann ein Exit-Proxy in diesem Land genutzt werden (niemals zur Umgehung von Rate-Limits)
python3 geo-audit/scripts/crawl_check.py https://example.com --proxy http://<Proxy>:<Port>
```

## Tests

```bash
python3 -m unittest discover -s geo-audit/tests -v
```
