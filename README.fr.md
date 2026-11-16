# geo-audit

[English](README.md) | [简体中文](README.zh-CN.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Deutsch](README.de.md) | **Français** | [Español](README.es.md)

Un skill au format ouvert Agent Skills. À partir d'une simple URL, il audite de l'extérieur la visibilité d'un site dans la recherche par IA sur un ou plusieurs pays ou marchés linguistiques (ChatGPT, Perplexity, Google AI Overviews, Gemini, Copilot, Doubao, DeepSeek, Naver AI Briefing, Le Chat, etc.) et produit un rapport d'optimisation dans lequel chaque recommandation est notée selon la force des preuves issues de la recherche. Le rapport est rédigé dans la langue de la demande.

- Marchés avec profil : Chine `cn`, États-Unis `us`, Japon `jp`, Corée du Sud `kr`, Allemagne `de`, France `fr`, marchés hispanophones `es` ; les autres marchés utilisent le profil générique

## Installation

```bash
# Installer dans le dépôt courant (Claude Code lit .claude/skills ; Codex et Cursor lisent .agents/skills)
bash geo-audit/install.sh

# Installer dans le répertoire personnel (pour tous les projets)
bash geo-audit/install.sh --user

# Installer dans un autre projet
bash geo-audit/install.sh --project /path/to/project

# Lier aussi dans le répertoire .cursor/skills propre à Cursor (généralement inutile ; Cursor lit aussi .agents/skills et .claude/skills)
bash geo-audit/install.sh --tools claude,agents,cursor
```

Le script d'installation ne crée que des liens symboliques ; les fichiers ou répertoires existants du même nom ne sont jamais écrasés.

## Utilisation dans chaque outil

Il suffit de demander en langage naturel, par exemple : "Fais un audit GEO de https://example.com pour les marchés français et américain"

| Outil | Remarques |
|---|---|
| Claude Code | Fonctionne directement. |
| Codex CLI | Activez la recherche web et l'accès réseau du bac à sable, sinon les scripts ne peuvent pas récupérer les pages et la section sur les mentions externes ne peut pas être vérifiée : `codex --search exec -s workspace-write -c sandbox_workspace_write.network_access=true "<votre demande>"` (En mode interactif, de même : `codex --search -s workspace-write -c sandbox_workspace_write.network_access=true`) |
| Cursor | Installation selon les répertoires documentés par Cursor (`.agents/skills` / `.claude/skills` / `.cursor/skills`). **Pas encore testé dans Cursor.** |

## Prérequis

- Python 3.10+ (bibliothèque standard uniquement)
- Facultatif : Chrome / Chromium pour la comparaison du rendu ; la variable `GEO_BROWSER` permet d'indiquer un navigateur précis

## Exécuter les scripts directement

```bash
python3 geo-audit/scripts/crawl_check.py https://example.com --markets jp,us
python3 geo-audit/scripts/page_audit.py https://example.com/ja/ --lang ja-JP --save-html out/html
python3 geo-audit/scripts/render_diff.py https://example.com/ja/ --lang ja-JP --timeout 30
# Pour tester l'accessibilité depuis un pays, on peut utiliser un proxy de sortie situé dans ce pays (jamais pour contourner les limites de débit)
python3 geo-audit/scripts/crawl_check.py https://example.com --proxy http://<proxy>:<port>
```

## Tests

```bash
python3 -m unittest discover -s geo-audit/tests -v
```
