# geo-audit

[简体中文](README.md) | [English](README.en.md) | [日本語](README.ja.md) | [한국어](README.ko.md) | [Deutsch](README.de.md) | [Français](README.fr.md) | **Español**

Un skill en el formato abierto Agent Skills. Con solo una URL, audita desde fuera la visibilidad de un sitio web en la búsqueda con IA en uno o varios países o mercados lingüísticos (ChatGPT, Perplexity, Google AI Overviews, Gemini, Copilot, Doubao, DeepSeek, Naver AI Briefing, Le Chat, etc.) y genera un informe de optimización en el que cada recomendación se califica según la solidez de la evidencia de investigación. El informe se redacta en el idioma en que se hizo la petición.

- Mercados con perfil: China `cn`, Estados Unidos `us`, Japón `jp`, Corea del Sur `kr`, Alemania `de`, Francia `fr`, mercados hispanohablantes `es`; el resto de mercados usan el perfil genérico

## Instalación

```bash
# Instalar en el repositorio actual (Claude Code lee .claude/skills; Codex y Cursor leen .agents/skills)
bash geo-audit/install.sh

# Instalar en el directorio personal (para todos los proyectos)
bash geo-audit/install.sh --user

# Instalar en otro proyecto
bash geo-audit/install.sh --project /path/to/project

# Enlazar también en el directorio propio de Cursor .cursor/skills (normalmente innecesario; Cursor también lee .agents/skills y .claude/skills)
bash geo-audit/install.sh --tools claude,agents,cursor
```

El instalador solo crea enlaces simbólicos; nunca sobrescribe archivos o directorios existentes con el mismo nombre.

## Uso en cada herramienta

Basta con pedirlo en lenguaje natural, por ejemplo: "Haz una auditoría GEO de https://example.com para los mercados de España y Estados Unidos"

| Herramienta | Notas |
|---|---|
| Claude Code | Funciona directamente. |
| Codex CLI | Activa la búsqueda web y el acceso a red del sandbox; si no, los scripts no pueden descargar páginas y la sección de menciones externas no se puede comprobar: `codex --search exec -s workspace-write -c sandbox_workspace_write.network_access=true "<tu petición>"` (En modo interactivo, igual: `codex --search -s workspace-write -c sandbox_workspace_write.network_access=true`) |
| Cursor | Instalación según los directorios documentados por Cursor (`.agents/skills` / `.claude/skills` / `.cursor/skills`). **Aún no probado en Cursor.** |

## Requisitos

- Python 3.10+ (solo biblioteca estándar)
- Opcional: Chrome / Chromium para la comparación de renderizado; con `GEO_BROWSER` se puede indicar un navegador concreto

## Ejecutar los scripts directamente

```bash
python3 geo-audit/scripts/crawl_check.py https://example.com --markets jp,us
python3 geo-audit/scripts/page_audit.py https://example.com/ja/ --lang ja-JP --save-html out/html
python3 geo-audit/scripts/render_diff.py https://example.com/ja/ --lang ja-JP --timeout 30
# Para probar la accesibilidad desde un país se puede usar un proxy de salida en ese país (nunca para evadir límites de velocidad)
python3 geo-audit/scripts/crawl_check.py https://example.com --proxy http://<proxy>:<puerto>
```

## Pruebas

```bash
python3 -m unittest discover -s geo-audit/tests -v
```
